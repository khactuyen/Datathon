from __future__ import annotations

import argparse
import json
import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.linear_model import HuberRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

try:
    from lightgbm import LGBMRegressor
except Exception:  # pragma: no cover - handled at runtime
    LGBMRegressor = None

try:
    from catboost import CatBoostRegressor
except Exception:  # pragma: no cover - handled at runtime
    CatBoostRegressor = None


warnings.filterwarnings("ignore")

RANDOM_SEED = 42
TARGETS = ["Revenue", "COGS"]
TRAIN_END_FOR_VALID = pd.Timestamp("2021-12-31")
VALID_START = pd.Timestamp("2022-01-01")
VALID_END = pd.Timestamp("2022-12-31")

LAGS = [1, 2, 3, 7, 14, 28, 56, 91, 182, 365]
ROLL_WINDOWS = [7, 14, 28, 56, 91, 182]
RESIDUAL_SHRINKAGE_GRID = [0.15, 0.25, 0.35, 0.50, 0.75, 1.00]
MONTH_SCALE_ALPHA_GRID = [0.15, 0.25, 0.35, 0.50]
ENSEMBLE_V3_WEIGHTS = [0.70, 0.80, 0.90]
PIPELINE_TAG = "v8"


@dataclass(frozen=True)
class ValidationFold:
    name: str
    train_end: pd.Timestamp
    valid_start: pd.Timestamp
    valid_end: pd.Timestamp
    calibration_year: int


VALIDATION_FOLDS = [
    ValidationFold(
        "F2020",
        pd.Timestamp("2019-12-31"),
        pd.Timestamp("2020-01-01"),
        pd.Timestamp("2020-12-31"),
        2020,
    ),
    ValidationFold(
        "F2021",
        pd.Timestamp("2020-12-31"),
        pd.Timestamp("2021-01-01"),
        pd.Timestamp("2021-12-31"),
        2021,
    ),
    ValidationFold(
        "F2022",
        pd.Timestamp("2021-12-31"),
        pd.Timestamp("2022-01-01"),
        pd.Timestamp("2022-12-31"),
        2022,
    ),
]


def find_project_root() -> Path:
    cwd = Path.cwd().resolve()
    for root in [cwd, *cwd.parents, Path(r"D:\DataThon")]:
        if (root / "dataset" / "sales.csv").exists() and (
            root / "dataset" / "sample_submission.csv"
        ).exists():
            return root
    raise FileNotFoundError("Cannot find dataset/sales.csv and dataset/sample_submission.csv")


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    dt = pd.to_datetime(out["Date"])
    out["year"] = dt.dt.year.astype(int)
    out["quarter"] = dt.dt.quarter.astype(int)
    out["month"] = dt.dt.month.astype(int)
    out["day"] = dt.dt.day.astype(int)
    out["doy"] = dt.dt.dayofyear.astype(int)
    out["dow"] = dt.dt.dayofweek.astype(int)
    out["weekofyear"] = dt.dt.isocalendar().week.astype(int)
    out["is_weekend"] = (out["dow"] >= 5).astype(int)
    out["is_month_start"] = dt.dt.is_month_start.astype(int)
    out["is_month_end"] = dt.dt.is_month_end.astype(int)
    out["is_quarter_start"] = dt.dt.is_quarter_start.astype(int)
    out["is_quarter_end"] = dt.dt.is_quarter_end.astype(int)
    out["is_year_start"] = dt.dt.is_year_start.astype(int)
    out["is_year_end"] = dt.dt.is_year_end.astype(int)
    out["time_idx"] = (dt - pd.Timestamp("2012-07-04")).dt.days.astype(int)

    out["dow_sin"] = np.sin(2 * np.pi * out["dow"] / 7.0)
    out["dow_cos"] = np.cos(2 * np.pi * out["dow"] / 7.0)
    out["month_sin"] = np.sin(2 * np.pi * out["month"] / 12.0)
    out["month_cos"] = np.cos(2 * np.pi * out["month"] / 12.0)
    out["doy_sin"] = np.sin(2 * np.pi * out["doy"] / 365.25)
    out["doy_cos"] = np.cos(2 * np.pi * out["doy"] / 365.25)
    return out


def load_inputs(project_root: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    sales = (
        pd.read_csv(project_root / "dataset" / "sales.csv", parse_dates=["Date"])
        .sort_values("Date")
        .reset_index(drop=True)
    )
    template = (
        pd.read_csv(project_root / "dataset" / "sample_submission.csv", parse_dates=["Date"])[
            ["Date", "Revenue", "COGS"]
        ]
        .sort_values("Date")
        .reset_index(drop=True)
    )

    expected_cols = ["Date", "Revenue", "COGS"]
    if list(sales.columns) != expected_cols:
        raise ValueError(f"sales.csv columns must be {expected_cols}, got {list(sales.columns)}")
    if list(template.columns) != expected_cols:
        raise ValueError(
            f"sample_submission.csv columns must be {expected_cols}, got {list(template.columns)}"
        )
    if not sales["Date"].is_monotonic_increasing:
        raise ValueError("sales.csv dates must be sorted")
    if sales[TARGETS].isna().any().any():
        raise ValueError("sales.csv contains missing targets")
    if (sales[TARGETS] < 0).any().any():
        raise ValueError("sales.csv contains negative targets")
    return sales, template


def evaluate_predictions(actual: np.ndarray, pred: np.ndarray) -> dict[str, float]:
    return {
        "MAE": float(mean_absolute_error(actual, pred)),
        "RMSE": float(mean_squared_error(actual, pred) ** 0.5),
        "R2": float(r2_score(actual, pred)),
    }


class SeasonalTrendForecaster:
    def __init__(self, seasonal_years: int, trend_years: int):
        self.seasonal_years = int(seasonal_years)
        self.trend_years = int(trend_years)

    def fit(self, train: pd.DataFrame) -> "SeasonalTrendForecaster":
        self.profile_md_: dict[str, pd.DataFrame] = {}
        self.profile_doy_: dict[str, pd.DataFrame] = {}
        self.last_level_: dict[str, float] = {}
        self.last_year_: dict[str, int] = {}
        self.trend_rate_: dict[str, float] = {}

        hist = add_calendar_features(train[["Date"] + TARGETS].copy())
        full_years = hist.groupby("year").filter(lambda x: len(x) >= 360).copy()
        if full_years.empty:
            raise ValueError("Need at least one complete year to fit seasonal profile")

        for target in TARGETS:
            annual = full_years.groupby("year")[target].mean().astype(float)
            self.last_year_[target] = int(annual.index.max())
            self.last_level_[target] = float(annual.iloc[-1])

            keep_years = annual.index[-min(self.seasonal_years, len(annual)) :]
            src = full_years[full_years["year"].isin(keep_years)].copy()
            src["seasonal_index"] = src[target] / src.groupby("year")[target].transform("mean")

            self.profile_md_[target] = (
                src.groupby(["month", "day"])["seasonal_index"].mean().reset_index()
            )
            self.profile_doy_[target] = (
                src.groupby("doy")["seasonal_index"]
                .mean()
                .reset_index(name="seasonal_index_doy")
            )

            if self.trend_years <= 0:
                self.trend_rate_[target] = 1.0
                continue

            trend_source = annual.tail(min(self.trend_years + 1, len(annual)))
            yoy = trend_source.pct_change().dropna()
            if len(yoy) == 0:
                self.trend_rate_[target] = 1.0
            else:
                self.trend_rate_[target] = float(np.exp(np.log1p(yoy).mean()))
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        future = add_calendar_features(
            pd.DataFrame({"Date": pd.to_datetime(dates)}).reset_index(drop=True)
        )
        out = future[["Date"]].copy()

        for target in TARGETS:
            tmp = future.merge(self.profile_md_[target], on=["month", "day"], how="left")
            tmp = tmp.merge(self.profile_doy_[target], on="doy", how="left")
            seasonal_index = (
                tmp["seasonal_index"].fillna(tmp["seasonal_index_doy"]).fillna(1.0).to_numpy(float)
            )
            years_ahead = tmp["year"].to_numpy(float) - self.last_year_[target]
            level = self.last_level_[target] * np.power(self.trend_rate_[target], years_ahead)
            out[target] = np.maximum(level * seasonal_index, 0.0)
        return out


def add_lag_features(df: pd.DataFrame, target: str) -> pd.DataFrame:
    out = add_calendar_features(df[["Date", target]].copy())
    shifted = out[target].shift(1)

    for lag in LAGS:
        out[f"{target}_lag_{lag}"] = out[target].shift(lag)

    for window in ROLL_WINDOWS:
        roll = shifted.rolling(window=window, min_periods=window)
        out[f"{target}_roll_mean_{window}"] = roll.mean()
        out[f"{target}_roll_std_{window}"] = roll.std()
        out[f"{target}_roll_min_{window}"] = roll.min()
        out[f"{target}_roll_max_{window}"] = roll.max()

    out[f"{target}_ewm_7"] = shifted.ewm(span=7, adjust=False, min_periods=7).mean()
    out[f"{target}_ewm_28"] = shifted.ewm(span=28, adjust=False, min_periods=28).mean()
    out[f"{target}_ewm_91"] = shifted.ewm(span=91, adjust=False, min_periods=91).mean()
    return out


@dataclass
class LGBMConfig:
    name: str
    params: dict[str, Any]


class RecursiveLGBMForecaster:
    def __init__(self, config: LGBMConfig):
        if LGBMRegressor is None:
            raise RuntimeError("lightgbm is not installed in this environment")
        self.config = config

    def fit(self, train: pd.DataFrame) -> "RecursiveLGBMForecaster":
        self.history_ = train[["Date"] + TARGETS].sort_values("Date").reset_index(drop=True)
        self.models_: dict[str, Any] = {}
        self.feature_columns_: dict[str, list[str]] = {}

        for target in TARGETS:
            frame = add_lag_features(self.history_[["Date", target]], target)
            feature_cols = [c for c in frame.columns if c not in ["Date", target]]
            fit_frame = frame.dropna(subset=feature_cols + [target]).copy()
            if len(fit_frame) < 200:
                raise ValueError(f"Not enough rows to train target {target}")

            model = LGBMRegressor(
                objective="regression",
                random_state=RANDOM_SEED,
                n_jobs=-1,
                verbosity=-1,
                **self.config.params,
            )
            model.fit(fit_frame[feature_cols], np.log1p(fit_frame[target].to_numpy(float)))
            self.models_[target] = model
            self.feature_columns_[target] = feature_cols
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        dates = pd.to_datetime(pd.Series(dates)).sort_values().reset_index(drop=True)
        history = self.history_.copy()
        rows = []

        for date in dates:
            row = {"Date": pd.Timestamp(date)}
            for target in TARGETS:
                tmp = pd.concat(
                    [
                        history[["Date", target]],
                        pd.DataFrame({"Date": [pd.Timestamp(date)], target: [np.nan]}),
                    ],
                    ignore_index=True,
                )
                feature_frame = add_lag_features(tmp, target)
                feature_cols = self.feature_columns_[target]
                x = feature_frame.loc[[len(feature_frame) - 1], feature_cols]
                pred = np.expm1(self.models_[target].predict(x)[0])
                row[target] = float(max(pred, 0.0))
            rows.append(row)
            history = pd.concat([history, pd.DataFrame([row])], ignore_index=True)

        return pd.DataFrame(rows)


class FixedBlendForecaster:
    def __init__(
        self,
        seasonal_years: int,
        trend_years: int,
        lgbm_config: LGBMConfig,
        lgbm_weight: float,
    ):
        self.seasonal_years = int(seasonal_years)
        self.trend_years = int(trend_years)
        self.lgbm_config = lgbm_config
        self.lgbm_weight = float(lgbm_weight)

    def fit(self, train: pd.DataFrame) -> "FixedBlendForecaster":
        self.seasonal_model_ = SeasonalTrendForecaster(
            self.seasonal_years, self.trend_years
        ).fit(train)
        self.lgbm_model_ = RecursiveLGBMForecaster(self.lgbm_config).fit(train)
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        seasonal = self.seasonal_model_.predict(dates)
        lgbm = self.lgbm_model_.predict(dates)
        out = seasonal[["Date"]].copy()
        for target in TARGETS:
            out[target] = (
                (1.0 - self.lgbm_weight) * seasonal[target]
                + self.lgbm_weight * lgbm[target]
            )
        return out


class WeekDowSeasonalForecaster:
    def __init__(self, seasonal_years: int, trend_years: int = 0):
        self.seasonal_years = int(seasonal_years)
        self.trend_years = int(trend_years)

    def fit(self, train: pd.DataFrame) -> "WeekDowSeasonalForecaster":
        self.profile_week_dow_: dict[str, pd.DataFrame] = {}
        self.profile_md_: dict[str, pd.DataFrame] = {}
        self.profile_dow_: dict[str, pd.DataFrame] = {}
        self.last_level_: dict[str, float] = {}
        self.last_year_: dict[str, int] = {}
        self.trend_rate_: dict[str, float] = {}

        hist = add_calendar_features(train[["Date"] + TARGETS].copy())
        full_years = hist.groupby("year").filter(lambda x: len(x) >= 360).copy()
        if full_years.empty:
            raise ValueError("Need at least one complete year to fit week/dow seasonal profile")

        for target in TARGETS:
            annual = full_years.groupby("year")[target].mean().astype(float)
            self.last_year_[target] = int(annual.index.max())
            self.last_level_[target] = float(annual.iloc[-1])

            keep_years = annual.index[-min(self.seasonal_years, len(annual)) :]
            src = full_years[full_years["year"].isin(keep_years)].copy()
            src["seasonal_index"] = src[target] / src.groupby("year")[target].transform("mean")

            self.profile_week_dow_[target] = (
                src.groupby(["weekofyear", "dow"])["seasonal_index"].mean().reset_index()
            )
            self.profile_md_[target] = (
                src.groupby(["month", "day"])["seasonal_index"].mean().reset_index(name="md_index")
            )
            self.profile_dow_[target] = (
                src.groupby("dow")["seasonal_index"].mean().reset_index(name="dow_index")
            )

            if self.trend_years <= 0:
                self.trend_rate_[target] = 1.0
            else:
                trend_source = annual.tail(min(self.trend_years + 1, len(annual)))
                yoy = trend_source.pct_change().dropna()
                self.trend_rate_[target] = float(np.exp(np.log1p(yoy).mean())) if len(yoy) else 1.0
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        future = add_calendar_features(
            pd.DataFrame({"Date": pd.to_datetime(dates)}).reset_index(drop=True)
        )
        out = future[["Date"]].copy()

        for target in TARGETS:
            tmp = future.merge(
                self.profile_week_dow_[target], on=["weekofyear", "dow"], how="left"
            )
            tmp = tmp.merge(self.profile_md_[target], on=["month", "day"], how="left")
            tmp = tmp.merge(self.profile_dow_[target], on="dow", how="left")
            seasonal_index = (
                tmp["seasonal_index"].fillna(tmp["md_index"]).fillna(tmp["dow_index"]).fillna(1.0)
            ).to_numpy(float)
            years_ahead = tmp["year"].to_numpy(float) - self.last_year_[target]
            level = self.last_level_[target] * np.power(self.trend_rate_[target], years_ahead)
            out[target] = np.maximum(level * seasonal_index, 0.0)
        return out


class CalendarSeasonalBlendForecaster:
    def __init__(self, seasonal_years: int, trend_years: int, week_weight: float):
        self.seasonal_years = int(seasonal_years)
        self.trend_years = int(trend_years)
        self.week_weight = float(week_weight)

    def fit(self, train: pd.DataFrame) -> "CalendarSeasonalBlendForecaster":
        self.month_day_model_ = SeasonalTrendForecaster(
            self.seasonal_years, self.trend_years
        ).fit(train)
        self.week_dow_model_ = WeekDowSeasonalForecaster(
            self.seasonal_years, self.trend_years
        ).fit(train)
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        month_day = self.month_day_model_.predict(dates)
        week_dow = self.week_dow_model_.predict(dates)
        out = month_day[["Date"]].copy()
        for target in TARGETS:
            out[target] = (
                (1.0 - self.week_weight) * month_day[target]
                + self.week_weight * week_dow[target]
            )
        return out


class TargetScaledForecaster:
    def __init__(self, base_forecaster: Any, target_scales: dict[str, float]):
        self.base_forecaster = base_forecaster
        self.target_scales = {target: float(target_scales[target]) for target in TARGETS}

    def fit(self, train: pd.DataFrame) -> "TargetScaledForecaster":
        self.base_forecaster.fit(train)
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        out = self.base_forecaster.predict(dates)
        for target in TARGETS:
            out[target] = out[target] * self.target_scales[target]
        return out


class MonthScaledForecaster:
    def __init__(self, base_forecaster: Any, month_scales: dict[str, dict[int, float]]):
        self.base_forecaster = base_forecaster
        self.month_scales = {
            target: {int(month): float(scale) for month, scale in scales.items()}
            for target, scales in month_scales.items()
        }

    def fit(self, train: pd.DataFrame) -> "MonthScaledForecaster":
        self.base_forecaster.fit(train)
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        out = self.base_forecaster.predict(dates)
        months = pd.to_datetime(out["Date"]).dt.month.astype(int)
        for target in TARGETS:
            scales = months.map(self.month_scales[target]).fillna(1.0).to_numpy(float)
            out[target] = out[target].to_numpy(float) * scales
        return out


class COGSRatioForecaster:
    def __init__(
        self,
        revenue_forecaster: Any,
        ratio_years: int = 6,
        ratio_week_weight: float = 0.25,
        clip_quantiles: tuple[float, float] = (0.01, 0.99),
    ):
        self.revenue_forecaster = revenue_forecaster
        self.ratio_years = int(ratio_years)
        self.ratio_week_weight = float(ratio_week_weight)
        self.clip_quantiles = clip_quantiles

    def fit(self, train: pd.DataFrame) -> "COGSRatioForecaster":
        train = train[["Date"] + TARGETS].sort_values("Date").reset_index(drop=True)
        self.revenue_forecaster.fit(train)
        ratio = (train["COGS"] / train["Revenue"].replace(0, np.nan)).replace(
            [np.inf, -np.inf], np.nan
        )
        ratio = ratio.ffill().bfill().clip(lower=0)
        low_q, high_q = self.clip_quantiles
        self.ratio_clip_low_ = float(ratio.quantile(low_q))
        self.ratio_clip_high_ = float(ratio.quantile(high_q))
        ratio_train = pd.DataFrame(
            {
                "Date": train["Date"],
                "Revenue": ratio.clip(self.ratio_clip_low_, self.ratio_clip_high_),
                "COGS": ratio.clip(self.ratio_clip_low_, self.ratio_clip_high_),
            }
        )
        self.ratio_model_ = CalendarSeasonalBlendForecaster(
            self.ratio_years, 0, self.ratio_week_weight
        ).fit(ratio_train)
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        revenue_pred = self.revenue_forecaster.predict(dates)
        ratio_pred = self.ratio_model_.predict(dates)["Revenue"].clip(
            self.ratio_clip_low_, self.ratio_clip_high_
        )
        out = revenue_pred[["Date"]].copy()
        out["Revenue"] = revenue_pred["Revenue"].to_numpy(float)
        out["COGS"] = np.maximum(out["Revenue"].to_numpy(float) * ratio_pred.to_numpy(float), 0.0)
        return out


class FixedEnsembleForecaster:
    def __init__(self, primary_forecaster: Any, secondary_forecaster: Any, primary_weight: float):
        self.primary_forecaster = primary_forecaster
        self.secondary_forecaster = secondary_forecaster
        self.primary_weight = float(primary_weight)

    def fit(self, train: pd.DataFrame) -> "FixedEnsembleForecaster":
        self.primary_forecaster.fit(train)
        self.secondary_forecaster.fit(train)
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        primary = self.primary_forecaster.predict(dates)
        secondary = self.secondary_forecaster.predict(dates)
        out = primary[["Date"]].copy()
        for target in TARGETS:
            out[target] = (
                self.primary_weight * primary[target].to_numpy(float)
                + (1.0 - self.primary_weight) * secondary[target].to_numpy(float)
            )
        return out


class ResidualMetaForecaster:
    """Learn a residual correction from the latest complete year.

    The base models learn the daily shape. The meta model learns how much each
    base forecast should influence the final residual correction.
    """

    def __init__(
        self,
        calibration_year: int | None = None,
        meta_model: str = "huber",
        feature_set: str = "base5",
        correction_shrinkage: float = 1.0,
    ):
        self.calibration_year = calibration_year
        self.meta_model = meta_model
        self.feature_set = feature_set
        self.correction_shrinkage = float(correction_shrinkage)
        self.base_model_factories = {
            "md4": lambda: SeasonalTrendForecaster(4, 0),
            "md5": lambda: SeasonalTrendForecaster(5, 0),
            "md6": lambda: SeasonalTrendForecaster(6, 0),
            "md7": lambda: SeasonalTrendForecaster(7, 0),
            "md8": lambda: SeasonalTrendForecaster(8, 0),
            "wd6": lambda: WeekDowSeasonalForecaster(6, 0),
            "wd7": lambda: WeekDowSeasonalForecaster(7, 0),
            "calblend6w25": lambda: CalendarSeasonalBlendForecaster(6, 0, 0.25),
            "calblend6w50": lambda: CalendarSeasonalBlendForecaster(6, 0, 0.50),
            "calblend7w25": lambda: CalendarSeasonalBlendForecaster(7, 0, 0.25),
        }
        self.residual_base_name = "calblend6w25"
        self.calendar_feature_columns = [
            "month",
            "day",
            "doy",
            "dow",
            "weekofyear",
            "is_weekend",
            "is_month_start",
            "is_month_end",
            "time_idx",
            "dow_sin",
            "dow_cos",
            "month_sin",
            "month_cos",
            "doy_sin",
            "doy_cos",
        ]

    def _select_calibration_year(self, train: pd.DataFrame) -> int:
        hist = add_calendar_features(train[["Date"] + TARGETS].copy())
        full_year_counts = hist.groupby("year").size()
        full_years = full_year_counts[full_year_counts >= 360].index.tolist()
        if not full_years:
            raise ValueError("Need at least one complete year for residual meta calibration")
        if self.calibration_year is not None:
            if self.calibration_year not in full_years:
                raise ValueError(f"Calibration year {self.calibration_year} is not complete")
            return int(self.calibration_year)
        return int(max(full_years))

    def _fit_base_models(self, train: pd.DataFrame) -> dict[str, Any]:
        return {name: factory().fit(train) for name, factory in self.base_model_factories.items()}

    def _base_feature_frame(
        self,
        dates: pd.Series | list[pd.Timestamp],
        fitted_models: dict[str, Any],
    ) -> pd.DataFrame:
        dates = pd.to_datetime(pd.Series(dates)).reset_index(drop=True)
        out = add_calendar_features(pd.DataFrame({"Date": dates}))

        for name, model in fitted_models.items():
            pred = model.predict(dates)
            for target in TARGETS:
                out[f"{name}_{target}"] = pred[target].to_numpy(float)

        for target in TARGETS:
            base_cols = [f"{name}_{target}" for name in self.base_model_factories]
            out[f"base_mean_{target}"] = out[base_cols].mean(axis=1)
            out[f"base_median_{target}"] = out[base_cols].median(axis=1)
            out[f"base_std_{target}"] = out[base_cols].std(axis=1)
            out[f"base_min_{target}"] = out[base_cols].min(axis=1)
            out[f"base_max_{target}"] = out[base_cols].max(axis=1)
        return out

    def _feature_columns(self, target: str) -> list[str]:
        if self.feature_set == "base5":
            names = ["md6", "wd6", "calblend6w25", "md7", "calblend7w25"]
            return [f"{name}_{target}" for name in names]

        if self.feature_set == "base5_cal":
            names = ["md6", "wd6", "calblend6w25", "md7", "calblend7w25"]
            return [f"{name}_{target}" for name in names] + self.calendar_feature_columns

        if self.feature_set == "base_all_cal":
            names = list(self.base_model_factories) + [
                "base_mean",
                "base_median",
                "base_std",
                "base_min",
                "base_max",
            ]
            return [f"{name}_{target}" for name in names] + self.calendar_feature_columns

        raise ValueError(f"Unknown residual meta feature_set: {self.feature_set}")

    def _make_meta_model(self) -> Any:
        if self.meta_model == "huber":
            return make_pipeline(
                StandardScaler(),
                HuberRegressor(alpha=0.001, epsilon=1.35, max_iter=1000),
            )

        if self.meta_model == "lgbm":
            if LGBMRegressor is None:
                raise RuntimeError("lightgbm is not installed in this environment")
            return LGBMRegressor(
                objective="mae",
                n_estimators=120,
                learning_rate=0.03,
                num_leaves=7,
                min_child_samples=20,
                reg_lambda=10.0,
                random_state=RANDOM_SEED,
                n_jobs=-1,
                verbosity=-1,
            )

        if self.meta_model == "catboost":
            if CatBoostRegressor is None:
                raise RuntimeError("catboost is not installed in this environment")
            return CatBoostRegressor(
                loss_function="MAE",
                iterations=220,
                learning_rate=0.03,
                depth=3,
                l2_leaf_reg=20,
                random_seed=RANDOM_SEED,
                verbose=False,
            )

        raise ValueError(f"Unknown residual meta_model: {self.meta_model}")

    def fit(self, train: pd.DataFrame) -> "ResidualMetaForecaster":
        train = train[["Date"] + TARGETS].sort_values("Date").reset_index(drop=True)
        self.calibration_year_ = self._select_calibration_year(train)
        cal_start = pd.Timestamp(f"{self.calibration_year_}-01-01")
        cal_end = pd.Timestamp(f"{self.calibration_year_}-12-31")

        base_train = train[train["Date"] < cal_start].copy()
        calibration = train[(train["Date"] >= cal_start) & (train["Date"] <= cal_end)].copy()
        if base_train.empty or len(calibration) < 360:
            raise ValueError("Not enough data to fit residual meta model")

        cal_base_models = self._fit_base_models(base_train)
        cal_features = self._base_feature_frame(calibration["Date"], cal_base_models)
        cal_features = cal_features.merge(calibration[["Date"] + TARGETS], on="Date")

        self.meta_models_: dict[str, Any] = {}
        self.feature_columns_: dict[str, list[str]] = {}
        self.training_rows_ = len(cal_features)

        calibration_prediction = cal_features[["Date"]].copy()
        for target in TARGETS:
            feature_cols = self._feature_columns(target)
            base_col = f"{self.residual_base_name}_{target}"
            residual = cal_features[target].to_numpy(float) - cal_features[base_col].to_numpy(float)
            model = self._make_meta_model()
            model.fit(cal_features[feature_cols], residual)
            self.meta_models_[target] = model
            self.feature_columns_[target] = feature_cols
            correction = self.correction_shrinkage * model.predict(cal_features[feature_cols])
            calibration_prediction[target] = np.maximum(
                cal_features[base_col].to_numpy(float) + correction,
                0.0,
            )

        self.calibration_prediction_ = calibration_prediction
        self.final_base_models_ = self._fit_base_models(train)
        return self

    def predict(self, dates: pd.Series | list[pd.Timestamp]) -> pd.DataFrame:
        features = self._base_feature_frame(dates, self.final_base_models_)
        out = features[["Date"]].copy()
        for target in TARGETS:
            base_col = f"{self.residual_base_name}_{target}"
            correction = self.correction_shrinkage * self.meta_models_[target].predict(
                features[self.feature_columns_[target]]
            )
            out[target] = np.maximum(features[base_col].to_numpy(float) + correction, 0.0)
        return out


def metric_rows(
    model: str,
    variant: str,
    pred: pd.DataFrame,
    valid: pd.DataFrame,
    extra: dict[str, Any] | None = None,
    train_start: pd.Timestamp | None = None,
    train_end: pd.Timestamp | None = None,
    valid_start: pd.Timestamp | None = None,
    valid_end: pd.Timestamp | None = None,
    fold: str | None = None,
) -> list[dict[str, Any]]:
    merged = valid[["Date"] + TARGETS].merge(
        pred[["Date"] + TARGETS], on="Date", suffixes=("_actual", "_pred")
    )
    train_end = train_end if train_end is not None else TRAIN_END_FOR_VALID
    valid_start = valid_start if valid_start is not None else VALID_START
    valid_end = valid_end if valid_end is not None else VALID_END
    rows = []
    for target in TARGETS:
        metrics = evaluate_predictions(
            merged[f"{target}_actual"].to_numpy(float), merged[f"{target}_pred"].to_numpy(float)
        )
        row = {
            "model": model,
            "variant": variant,
            "target": target,
            "fold": fold,
            "train_start": train_start.date().isoformat() if train_start is not None else None,
            "train_end": train_end.date().isoformat(),
            "valid_start": valid_start.date().isoformat(),
            "valid_end": valid_end.date().isoformat(),
            **metrics,
        }
        if extra:
            row.update(extra)
        rows.append(row)
    return rows


def optimize_target_scales(
    valid: pd.DataFrame,
    pred: pd.DataFrame,
    low: float = 0.85,
    high: float = 1.25,
    step: float = 0.001,
) -> tuple[dict[str, float], pd.DataFrame]:
    scaled = pred.copy()
    scales: dict[str, float] = {}
    grid = np.arange(low, high + step / 2, step)

    for target in TARGETS:
        actual = valid[target].to_numpy(float)
        base = pred[target].to_numpy(float)
        maes = [mean_absolute_error(actual, base * scale) for scale in grid]
        best_scale = float(grid[int(np.argmin(maes))])
        scales[target] = best_scale
        scaled[target] = base * best_scale
    return scales, scaled


def optimize_month_target_scales(
    valid: pd.DataFrame,
    pred: pd.DataFrame,
    global_scales: dict[str, float],
    alpha: float,
    low: float = 0.85,
    high: float = 1.25,
    step: float = 0.001,
) -> tuple[dict[str, dict[int, float]], pd.DataFrame]:
    scaled = pred.copy()
    month_scales: dict[str, dict[int, float]] = {target: {} for target in TARGETS}
    grid = np.arange(low, high + step / 2, step)
    months = pd.to_datetime(valid["Date"]).dt.month.astype(int)

    for target in TARGETS:
        target_scaled = pred[target].copy()
        for month in range(1, 13):
            mask = months.to_numpy() == month
            if not mask.any():
                month_scales[target][month] = float(global_scales[target])
                continue
            actual = valid[target].to_numpy(float)[mask]
            base = pred[target].to_numpy(float)[mask]
            maes = [mean_absolute_error(actual, base * scale) for scale in grid]
            best_month_scale = float(grid[int(np.argmin(maes))])
            final_scale = float(global_scales[target] * (1.0 - alpha) + best_month_scale * alpha)
            month_scales[target][month] = final_scale
            target_scaled.iloc[np.where(mask)[0]] = base * final_scale
        scaled[target] = target_scaled
    return month_scales, scaled


def add_combined_scores(metrics: pd.DataFrame) -> pd.DataFrame:
    summary = (
        metrics.groupby(["model", "variant"], as_index=False)
        .agg(MAE_sum=("MAE", "sum"), RMSE_sum=("RMSE", "sum"), R2_mean=("R2", "mean"))
        .sort_values(["MAE_sum", "RMSE_sum"])
        .reset_index(drop=True)
    )
    summary["rank"] = np.arange(1, len(summary) + 1)
    return metrics.merge(summary, on=["model", "variant"], how="left")


def summarize_guardrail_metrics(metrics: pd.DataFrame) -> pd.DataFrame:
    by_fold = (
        metrics.groupby(["model", "variant", "fold"], as_index=False)
        .agg(MAE_sum=("MAE", "sum"), RMSE_sum=("RMSE", "sum"), R2_mean=("R2", "mean"))
        .sort_values(["model", "variant", "fold"])
    )
    summary = (
        by_fold.groupby(["model", "variant"], as_index=False)
        .agg(
            guardrail_avg_MAE_sum=("MAE_sum", "mean"),
            guardrail_worst_MAE_sum=("MAE_sum", "max"),
            guardrail_avg_RMSE_sum=("RMSE_sum", "mean"),
            guardrail_avg_R2_mean=("R2_mean", "mean"),
        )
        .sort_values(["guardrail_avg_MAE_sum", "guardrail_worst_MAE_sum"])
        .reset_index(drop=True)
    )
    summary["guardrail_rank"] = np.arange(1, len(summary) + 1)
    return summary


def add_anchor_mean_ratios(
    metrics: pd.DataFrame,
    predictions_by_key: dict[tuple[str, str], pd.DataFrame],
    anchor_key: tuple[str, str],
) -> pd.DataFrame:
    if anchor_key not in predictions_by_key:
        return metrics

    anchor = predictions_by_key[anchor_key]
    rows = []
    for key, pred in predictions_by_key.items():
        row = {"model": key[0], "variant": key[1]}
        for target in TARGETS:
            denom = float(anchor[target].mean())
            row[f"valid_{target.lower()}_mean_ratio_vs_v3"] = (
                float(pred[target].mean() / denom) if denom else np.nan
            )
        rows.append(row)
    ratios = pd.DataFrame(rows)
    return metrics.merge(ratios, on=["model", "variant"], how="left")


def validate_submission(submission: pd.DataFrame, template: pd.DataFrame) -> None:
    expected_dates = template["Date"].dt.strftime("%Y-%m-%d").tolist()
    if list(submission.columns) != ["Date", "Revenue", "COGS"]:
        raise ValueError("Submission columns must be Date, Revenue, COGS")
    if len(submission) != len(template):
        raise ValueError("Submission row count differs from sample_submission.csv")
    if submission["Date"].tolist() != expected_dates:
        raise ValueError("Submission date order differs from sample_submission.csv")
    if submission[TARGETS].isna().any().any():
        raise ValueError("Submission contains missing predictions")
    if (submission[TARGETS] < 0).any().any():
        raise ValueError("Submission contains negative predictions")


def choose_best_guarded_config(
    metrics: pd.DataFrame,
    guardrail_summary: pd.DataFrame | None,
    anchor_key: tuple[str, str],
) -> tuple[str, str]:
    summary = (
        metrics.groupby(["model", "variant"], as_index=False)
        .agg(
            MAE_sum=("MAE", "sum"),
            RMSE_sum=("RMSE", "sum"),
            meta_shrinkage=("meta_shrinkage", "max"),
        )
        .sort_values(["MAE_sum", "RMSE_sum"])
        .reset_index(drop=True)
    )
    if guardrail_summary is not None and not guardrail_summary.empty:
        summary = summary.merge(guardrail_summary, on=["model", "variant"], how="left")
        anchor = guardrail_summary[
            (guardrail_summary["model"] == anchor_key[0])
            & (guardrail_summary["variant"] == anchor_key[1])
        ]
        if not anchor.empty:
            anchor_avg = float(anchor.iloc[0]["guardrail_avg_MAE_sum"])
            summary["guardrail_ok"] = (
                summary["guardrail_avg_MAE_sum"].notna()
                & (summary["guardrail_avg_MAE_sum"] <= anchor_avg * 1.02)
            )
        else:
            summary["guardrail_ok"] = summary["guardrail_avg_MAE_sum"].notna()
    else:
        summary["guardrail_ok"] = True

    high_risk_external = (
        ((summary["model"] == "residual_meta_lgbm") & (summary["meta_shrinkage"].fillna(0.0) > 0.50))
        | (
            (summary["model"] == "residual_meta_catboost")
            & (summary["meta_shrinkage"].fillna(0.0) >= 1.0)
        )
    )
    eligible = summary[summary["guardrail_ok"] & ~high_risk_external].copy()
    if eligible.empty:
        eligible = summary.copy()
    eligible = eligible.sort_values(
        ["guardrail_avg_MAE_sum", "MAE_sum", "RMSE_sum"], na_position="last"
    ).reset_index(drop=True)
    return str(eligible.loc[0, "model"]), str(eligible.loc[0, "variant"])


def build_backtest_table(best_pred: pd.DataFrame, valid: pd.DataFrame, model: str, variant: str) -> pd.DataFrame:
    out = valid[["Date"] + TARGETS].merge(
        best_pred[["Date"] + TARGETS], on="Date", suffixes=("_actual", "_pred")
    )
    out.insert(1, "model", model)
    out.insert(2, "variant", variant)
    for target in TARGETS:
        out[f"{target}_error"] = out[f"{target}_pred"] - out[f"{target}_actual"]
        out[f"{target}_abs_error"] = out[f"{target}_error"].abs()
    return out


def choose_best_config(metrics: pd.DataFrame) -> tuple[str, str]:
    summary = (
        metrics.groupby(["model", "variant"], as_index=False)
        .agg(MAE_sum=("MAE", "sum"), RMSE_sum=("RMSE", "sum"))
        .sort_values(["MAE_sum", "RMSE_sum"])
        .reset_index(drop=True)
    )
    return str(summary.loc[0, "model"]), str(summary.loc[0, "variant"])


def fold_train_valid(sales: pd.DataFrame, fold: ValidationFold) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = sales[sales["Date"] <= fold.train_end].copy()
    valid = sales[(sales["Date"] >= fold.valid_start) & (sales["Date"] <= fold.valid_end)].copy()
    if train.empty or valid.empty:
        raise ValueError(f"Fold {fold.name} is missing train or validation rows")
    return train, valid


def predict_fold_v3_scaled(sales: pd.DataFrame, fold: ValidationFold) -> pd.DataFrame:
    train, valid = fold_train_valid(sales, fold)
    base = CalendarSeasonalBlendForecaster(6, 0, 0.25).fit(train)
    base_pred = base.predict(valid["Date"])
    _, scaled_pred = optimize_target_scales(valid, base_pred)
    return scaled_pred


def predict_fold_month_scaled(
    sales: pd.DataFrame, fold: ValidationFold, alpha: float
) -> pd.DataFrame:
    train, valid = fold_train_valid(sales, fold)
    base = CalendarSeasonalBlendForecaster(6, 0, 0.25).fit(train)
    base_pred = base.predict(valid["Date"])
    global_scales, _ = optimize_target_scales(valid, base_pred)
    _, month_pred = optimize_month_target_scales(valid, base_pred, global_scales, alpha)
    return month_pred


def predict_fold_residual_meta(
    sales: pd.DataFrame,
    fold: ValidationFold,
    meta_model: str,
    feature_set: str,
    shrinkage: float,
) -> pd.DataFrame:
    fold_sales = sales[sales["Date"] <= fold.valid_end].copy()
    model = ResidualMetaForecaster(
        calibration_year=fold.calibration_year,
        meta_model=meta_model,
        feature_set=feature_set,
        correction_shrinkage=shrinkage,
    ).fit(fold_sales)
    return model.calibration_prediction_


def predict_fold_cogs_ratio(sales: pd.DataFrame, fold: ValidationFold) -> pd.DataFrame:
    train, valid = fold_train_valid(sales, fold)
    base = CalendarSeasonalBlendForecaster(6, 0, 0.25).fit(train)
    base_pred = base.predict(valid["Date"])
    scales, scaled_pred = optimize_target_scales(valid, base_pred)

    ratio_train = train.copy()
    ratio = (ratio_train["COGS"] / ratio_train["Revenue"].replace(0, np.nan)).replace(
        [np.inf, -np.inf], np.nan
    )
    ratio_train["Revenue"] = ratio.ffill().bfill().clip(lower=0)
    ratio_train["COGS"] = ratio_train["Revenue"]
    ratio_model = CalendarSeasonalBlendForecaster(6, 0, 0.25).fit(ratio_train)
    ratio_pred = ratio_model.predict(valid["Date"])["Revenue"]
    ratio_low = float(ratio_train["Revenue"].quantile(0.01))
    ratio_high = float(ratio_train["Revenue"].quantile(0.99))

    out = scaled_pred[["Date", "Revenue"]].copy()
    out["COGS"] = np.maximum(
        out["Revenue"].to_numpy(float) * ratio_pred.clip(ratio_low, ratio_high).to_numpy(float),
        0.0,
    )
    _ = scales
    return out


def run_guardrail_validation(
    sales: pd.DataFrame,
    fold_predictors: dict[tuple[str, str], Any],
) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows: list[dict[str, Any]] = []
    for key, predictor in fold_predictors.items():
        for fold in VALIDATION_FOLDS:
            train, valid = fold_train_valid(sales, fold)
            pred = predictor(sales, fold)
            rows.extend(
                metric_rows(
                    key[0],
                    key[1],
                    pred,
                    valid,
                    train_start=train["Date"].min(),
                    train_end=fold.train_end,
                    valid_start=fold.valid_start,
                    valid_end=fold.valid_end,
                    fold=fold.name,
                )
            )
    guardrail_metrics = pd.DataFrame(rows)
    return guardrail_metrics, summarize_guardrail_metrics(guardrail_metrics)


def predict_fold_ensemble(
    sales: pd.DataFrame,
    fold: ValidationFold,
    primary_predictor: Any,
    secondary_predictor: Any,
    primary_weight: float,
) -> pd.DataFrame:
    primary = primary_predictor(sales, fold)
    secondary = secondary_predictor(sales, fold)
    out = primary[["Date"]].copy()
    for target in TARGETS:
        out[target] = (
            primary_weight * primary[target].to_numpy(float)
            + (1.0 - primary_weight) * secondary[target].to_numpy(float)
        )
    return out


def run_pipeline(project_root: Path) -> None:
    np.random.seed(RANDOM_SEED)
    sales, template = load_inputs(project_root)
    train_valid = sales[sales["Date"] <= TRAIN_END_FOR_VALID].copy()
    valid = sales[(sales["Date"] >= VALID_START) & (sales["Date"] <= VALID_END)].copy()

    if valid.empty or valid["Date"].min() != VALID_START or valid["Date"].max() != VALID_END:
        raise ValueError("Validation period 2022-01-01 to 2022-12-31 is not complete")

    output_dir = project_root / "submition"
    output_dir.mkdir(exist_ok=True)

    metrics_rows: list[dict[str, Any]] = []
    predictions_by_key: dict[tuple[str, str], pd.DataFrame] = {}
    forecaster_builders: dict[tuple[str, str], Any] = {}
    scale_candidate_keys: list[tuple[str, str]] = []
    target_scales_by_base_key: dict[tuple[str, str], dict[str, float]] = {}
    fold_predictors: dict[tuple[str, str], Any] = {}
    anchor_base_key = ("calendar_blend", "seasonal6_week25_trend0")
    anchor_scaled_key = ("calendar_blend_valid_scaled", "seasonal6_week25_trend0_scaled")
    safe_ensemble_secondary_keys: list[tuple[str, str]] = []

    seasonal_year_grid = [3, 4, 5, 6, 7, 8, 9, 10]
    trend_year_grid = [0, 2, 3, 5, 8]
    for seasonal_years in seasonal_year_grid:
        for trend_years in trend_year_grid:
            variant = f"seasonal{seasonal_years}_trend{trend_years}"
            model = SeasonalTrendForecaster(seasonal_years, trend_years).fit(train_valid)
            pred = model.predict(valid["Date"])
            key = ("seasonal_profile", variant)
            predictions_by_key[key] = pred
            forecaster_builders[key] = lambda s=seasonal_years, t=trend_years: SeasonalTrendForecaster(s, t)
            if trend_years == 0:
                scale_candidate_keys.append(key)
            metrics_rows.extend(
                metric_rows(
                    "seasonal_profile",
                    variant,
                    pred,
                    valid,
                    {"seasonal_years": seasonal_years, "trend_years": trend_years},
                )
            )

    for seasonal_years in [5, 6, 7, 8]:
        for week_weight in [0.25, 0.50, 0.75]:
            variant = f"seasonal{seasonal_years}_week{int(week_weight * 100):02d}_trend0"
            model = CalendarSeasonalBlendForecaster(seasonal_years, 0, week_weight).fit(
                train_valid
            )
            pred = model.predict(valid["Date"])
            key = ("calendar_blend", variant)
            predictions_by_key[key] = pred
            forecaster_builders[key] = (
                lambda s=seasonal_years, w=week_weight: CalendarSeasonalBlendForecaster(s, 0, w)
            )
            scale_candidate_keys.append(key)
            metrics_rows.extend(
                metric_rows(
                    "calendar_blend",
                    variant,
                    pred,
                    valid,
                    {
                        "seasonal_years": seasonal_years,
                        "trend_years": 0,
                        "week_weight": week_weight,
                    },
                )
            )

    lgbm_configs = [
        LGBMConfig(
            "lgbm_stable",
            {
                "n_estimators": 700,
                "learning_rate": 0.035,
                "num_leaves": 31,
                "min_child_samples": 35,
                "subsample": 0.9,
                "colsample_bytree": 0.9,
                "reg_lambda": 2.0,
            },
        ),
        LGBMConfig(
            "lgbm_smooth",
            {
                "n_estimators": 550,
                "learning_rate": 0.03,
                "num_leaves": 15,
                "min_child_samples": 60,
                "subsample": 0.95,
                "colsample_bytree": 0.85,
                "reg_lambda": 6.0,
            },
        ),
        LGBMConfig(
            "lgbm_flexible",
            {
                "n_estimators": 850,
                "learning_rate": 0.025,
                "num_leaves": 63,
                "min_child_samples": 25,
                "subsample": 0.85,
                "colsample_bytree": 0.95,
                "reg_lambda": 1.0,
            },
        ),
    ]

    if LGBMRegressor is not None:
        for cfg in lgbm_configs:
            model = RecursiveLGBMForecaster(cfg).fit(train_valid)
            pred = model.predict(valid["Date"])
            key = ("recursive_lgbm", cfg.name)
            predictions_by_key[key] = pred
            forecaster_builders[key] = lambda c=cfg: RecursiveLGBMForecaster(c)
            metrics_rows.extend(
                metric_rows("recursive_lgbm", cfg.name, pred, valid, {"lgbm_config": cfg.name})
            )

        metrics_so_far = pd.DataFrame(metrics_rows)
        seasonal_best_key = choose_best_config(
            metrics_so_far[metrics_so_far["model"] == "seasonal_profile"]
        )
        lgbm_best_key = choose_best_config(metrics_so_far[metrics_so_far["model"] == "recursive_lgbm"])
        seasonal_best = predictions_by_key[seasonal_best_key]
        lgbm_best = predictions_by_key[lgbm_best_key]
        seasonal_parts = seasonal_best_key[1].replace("seasonal", "").split("_trend")
        best_seasonal_years = int(seasonal_parts[0])
        best_trend_years = int(seasonal_parts[1])
        best_lgbm_cfg = next(cfg for cfg in lgbm_configs if cfg.name == lgbm_best_key[1])

        for weight in [0.25, 0.40, 0.50, 0.60, 0.75]:
            pred = seasonal_best[["Date"]].copy()
            for target in TARGETS:
                pred[target] = (1.0 - weight) * seasonal_best[target] + weight * lgbm_best[target]
            variant = f"seasonal_lgbm_w{int(weight * 100):02d}"
            key = ("blend", variant)
            predictions_by_key[key] = pred
            forecaster_builders[key] = lambda w=weight: FixedBlendForecaster(
                best_seasonal_years, best_trend_years, best_lgbm_cfg, w
            )
            metrics_rows.extend(
                metric_rows(
                    "blend",
                    variant,
                    pred,
                    valid,
                    {
                        "seasonal_years": best_seasonal_years,
                        "trend_years": best_trend_years,
                        "lgbm_config": best_lgbm_cfg.name,
                        "lgbm_weight": weight,
                    },
                )
            )

    for base_key in list(scale_candidate_keys):
        base_model, base_variant = base_key
        base_pred = predictions_by_key[base_key]
        target_scales, scaled_pred = optimize_target_scales(valid, base_pred)
        target_scales_by_base_key[base_key] = target_scales
        variant = f"{base_variant}_scaled"
        key = (f"{base_model}_valid_scaled", variant)
        base_builder = forecaster_builders[base_key]
        predictions_by_key[key] = scaled_pred
        forecaster_builders[key] = (
            lambda builder=base_builder, scales=target_scales: TargetScaledForecaster(
                builder(), scales
            )
        )
        metrics_rows.extend(
            metric_rows(
                key[0],
                variant,
                scaled_pred,
                valid,
                {
                    "calibrated_on_valid": True,
                    "base_model": base_model,
                    "base_variant": base_variant,
                    "scale_source": "2022_validation",
                    "revenue_scale": target_scales["Revenue"],
                    "cogs_scale": target_scales["COGS"],
                },
            )
        )
        if base_key == anchor_base_key:
            fold_predictors[key] = predict_fold_v3_scaled

    if anchor_base_key in predictions_by_key and anchor_base_key in target_scales_by_base_key:
        anchor_base_builder = forecaster_builders[anchor_base_key]
        anchor_base_pred = predictions_by_key[anchor_base_key]
        anchor_scales = target_scales_by_base_key[anchor_base_key]

        for alpha in MONTH_SCALE_ALPHA_GRID:
            month_scales, month_pred = optimize_month_target_scales(
                valid, anchor_base_pred, anchor_scales, alpha
            )
            variant = f"seasonal6_week25_trend0_month_alpha{int(alpha * 100):02d}"
            key = ("calendar_blend_month_scaled", variant)
            predictions_by_key[key] = month_pred
            forecaster_builders[key] = (
                lambda builder=anchor_base_builder, scales=month_scales: MonthScaledForecaster(
                    builder(), scales
                )
            )
            fold_predictors[key] = (
                lambda sales_df, fold, a=alpha: predict_fold_month_scaled(sales_df, fold, a)
            )
            metrics_rows.extend(
                metric_rows(
                    key[0],
                    key[1],
                    month_pred,
                    valid,
                    {
                        "calibrated_on_valid": True,
                        "base_model": anchor_base_key[0],
                        "base_variant": anchor_base_key[1],
                        "scale_source": "2022_validation_month_shrink",
                        "revenue_scale": anchor_scales["Revenue"],
                        "cogs_scale": anchor_scales["COGS"],
                        "month_scale_alpha": alpha,
                    },
                )
            )

        cogs_ratio_revenue_forecaster = TargetScaledForecaster(
            CalendarSeasonalBlendForecaster(6, 0, 0.25), anchor_scales
        )
        cogs_ratio_pred = COGSRatioForecaster(cogs_ratio_revenue_forecaster).fit(
            train_valid
        ).predict(valid["Date"])
        key = ("cogs_ratio", "v3_revenue_ratio_profile")
        predictions_by_key[key] = cogs_ratio_pred
        forecaster_builders[key] = (
            lambda scales=anchor_scales: COGSRatioForecaster(
                TargetScaledForecaster(CalendarSeasonalBlendForecaster(6, 0, 0.25), scales)
            )
        )
        fold_predictors[key] = predict_fold_cogs_ratio
        metrics_rows.extend(
            metric_rows(
                key[0],
                key[1],
                cogs_ratio_pred,
                valid,
                {
                    "calibrated_on_valid": True,
                    "base_model": anchor_scaled_key[0],
                    "base_variant": anchor_scaled_key[1],
                    "ratio_model": "calendar_blend_ratio_profile",
                },
            )
        )

    residual_meta = ResidualMetaForecaster(calibration_year=2022).fit(sales)
    key = ("residual_meta", "huber_base_forecasts_cal2022")
    predictions_by_key[key] = residual_meta.calibration_prediction_
    forecaster_builders[key] = lambda: ResidualMetaForecaster(calibration_year=2022)
    fold_predictors[key] = (
        lambda sales_df, fold: predict_fold_residual_meta(
            sales_df, fold, "huber", "base5", 1.0
        )
    )
    metrics_rows.extend(
        metric_rows(
            key[0],
            key[1],
            residual_meta.calibration_prediction_,
            valid,
            {
                "calibrated_on_valid": True,
                "meta_model": "HuberRegressor",
                "meta_target": "residual",
                "meta_features": "md6,wd6,calblend6w25,md7,calblend7w25",
                "meta_feature_set": "base5",
                "meta_shrinkage": 1.0,
                "calibration_year": 2022,
                "base_variant": "calblend6w25",
            },
        )
    )

    if LGBMRegressor is not None:
        for feature_set in ["base_all_cal", "base5_cal"]:
            for shrinkage in RESIDUAL_SHRINKAGE_GRID:
                residual_lgbm = ResidualMetaForecaster(
                    calibration_year=2022,
                    meta_model="lgbm",
                    feature_set=feature_set,
                    correction_shrinkage=shrinkage,
                ).fit(sales)
                variant = f"lgbm_{feature_set}_sh{int(shrinkage * 100):03d}_cal2022"
                key = ("residual_meta_lgbm", variant)
                predictions_by_key[key] = residual_lgbm.calibration_prediction_
                forecaster_builders[key] = (
                    lambda fs=feature_set, sh=shrinkage: ResidualMetaForecaster(
                        calibration_year=2022,
                        meta_model="lgbm",
                        feature_set=fs,
                        correction_shrinkage=sh,
                    )
                )
                fold_predictors[key] = (
                    lambda sales_df, fold, fs=feature_set, sh=shrinkage: predict_fold_residual_meta(
                        sales_df, fold, "lgbm", fs, sh
                    )
                )
                metrics_rows.extend(
                    metric_rows(
                        key[0],
                        key[1],
                        residual_lgbm.calibration_prediction_,
                        valid,
                        {
                            "calibrated_on_valid": True,
                            "meta_model": "LightGBMRegressor",
                            "meta_target": "residual",
                            "meta_features": feature_set,
                            "meta_feature_set": feature_set,
                            "meta_shrinkage": shrinkage,
                            "calibration_year": 2022,
                            "base_variant": "calblend6w25",
                        },
                    )
                )

    if CatBoostRegressor is not None:
        for feature_set in ["base_all_cal", "base5_cal", "base5"]:
            for shrinkage in RESIDUAL_SHRINKAGE_GRID:
                residual_cat = ResidualMetaForecaster(
                    calibration_year=2022,
                    meta_model="catboost",
                    feature_set=feature_set,
                    correction_shrinkage=shrinkage,
                ).fit(sales)
                variant = f"catboost_{feature_set}_sh{int(shrinkage * 100):03d}_cal2022"
                key = ("residual_meta_catboost", variant)
                predictions_by_key[key] = residual_cat.calibration_prediction_
                forecaster_builders[key] = (
                    lambda fs=feature_set, sh=shrinkage: ResidualMetaForecaster(
                        calibration_year=2022,
                        meta_model="catboost",
                        feature_set=fs,
                        correction_shrinkage=sh,
                    )
                )
                fold_predictors[key] = (
                    lambda sales_df, fold, fs=feature_set, sh=shrinkage: predict_fold_residual_meta(
                        sales_df, fold, "catboost", fs, sh
                    )
                )
                if feature_set == "base_all_cal" and shrinkage in [0.25, 0.50, 0.75]:
                    safe_ensemble_secondary_keys.append(key)
                metrics_rows.extend(
                    metric_rows(
                        key[0],
                        key[1],
                        residual_cat.calibration_prediction_,
                        valid,
                        {
                            "calibrated_on_valid": True,
                            "meta_model": "CatBoostRegressor",
                            "meta_target": "residual",
                            "meta_features": feature_set,
                            "meta_feature_set": feature_set,
                            "meta_shrinkage": shrinkage,
                            "calibration_year": 2022,
                            "base_variant": "calblend6w25",
                        },
                    )
                )

    if anchor_scaled_key in predictions_by_key and anchor_scaled_key in forecaster_builders:
        anchor_pred = predictions_by_key[anchor_scaled_key]
        anchor_builder = forecaster_builders[anchor_scaled_key]
        for secondary_key in safe_ensemble_secondary_keys:
            if secondary_key not in predictions_by_key:
                continue
            secondary_pred = predictions_by_key[secondary_key]
            secondary_builder = forecaster_builders[secondary_key]
            secondary_fold_predictor = fold_predictors.get(secondary_key)
            for v3_weight in ENSEMBLE_V3_WEIGHTS:
                pred = anchor_pred[["Date"]].copy()
                for target in TARGETS:
                    pred[target] = (
                        v3_weight * anchor_pred[target].to_numpy(float)
                        + (1.0 - v3_weight) * secondary_pred[target].to_numpy(float)
                    )
                variant = (
                    f"v3w{int(v3_weight * 100):02d}_"
                    f"{secondary_key[1].replace('_cal2022', '')}"
                )
                key = ("ensemble_v3_catboost", variant)
                predictions_by_key[key] = pred
                forecaster_builders[key] = (
                    lambda ab=anchor_builder, sb=secondary_builder, w=v3_weight: FixedEnsembleForecaster(
                        ab(), sb(), w
                    )
                )
                if secondary_fold_predictor is not None:
                    fold_predictors[key] = (
                        lambda sales_df, fold, sfp=secondary_fold_predictor, w=v3_weight: predict_fold_ensemble(
                            sales_df, fold, predict_fold_v3_scaled, sfp, w
                        )
                    )
                metrics_rows.extend(
                    metric_rows(
                        key[0],
                        key[1],
                        pred,
                        valid,
                        {
                            "calibrated_on_valid": True,
                            "base_model": anchor_scaled_key[0],
                            "base_variant": anchor_scaled_key[1],
                            "ensemble_secondary_model": secondary_key[0],
                            "ensemble_secondary_variant": secondary_key[1],
                            "v3_weight": v3_weight,
                        },
                    )
                )

    metrics = add_combined_scores(pd.DataFrame(metrics_rows))
    metrics["train_start"] = metrics["train_start"].fillna(
        train_valid["Date"].min().date().isoformat()
    )
    metrics = add_anchor_mean_ratios(metrics, predictions_by_key, anchor_scaled_key)
    metrics = metrics.sort_values(["rank", "target"]).reset_index(drop=True)
    guardrail_metrics, guardrail_summary = run_guardrail_validation(sales, fold_predictors)

    metrics_file = project_root / f"model_comparison_valid_{PIPELINE_TAG}.csv"
    try:
        metrics.to_csv(metrics_file, index=False)
    except PermissionError:
        metrics_file = project_root / f"model_comparison_valid_{PIPELINE_TAG}_locked_fallback.csv"
        metrics.to_csv(metrics_file, index=False)

    guardrail_metrics_file = project_root / f"guardrail_fold_metrics_{PIPELINE_TAG}.csv"
    guardrail_summary_file = project_root / f"guardrail_summary_{PIPELINE_TAG}.csv"
    try:
        guardrail_metrics.to_csv(guardrail_metrics_file, index=False)
        guardrail_summary.to_csv(guardrail_summary_file, index=False)
    except PermissionError:
        guardrail_metrics_file = project_root / f"guardrail_fold_metrics_{PIPELINE_TAG}_locked_fallback.csv"
        guardrail_summary_file = project_root / f"guardrail_summary_{PIPELINE_TAG}_locked_fallback.csv"
        guardrail_metrics.to_csv(guardrail_metrics_file, index=False)
        guardrail_summary.to_csv(guardrail_summary_file, index=False)

    best_model, best_variant = choose_best_guarded_config(
        metrics, guardrail_summary, anchor_scaled_key
    )
    best_key = (best_model, best_variant)
    backtest = build_backtest_table(predictions_by_key[best_key], valid, best_model, best_variant)
    backtest_file = project_root / f"optimization_backtest_{PIPELINE_TAG}.csv"
    try:
        backtest.to_csv(backtest_file, index=False)
    except PermissionError:
        backtest_file = project_root / f"optimization_backtest_{PIPELINE_TAG}_locked_fallback.csv"
        backtest.to_csv(backtest_file, index=False)

    final_forecaster = forecaster_builders[best_key]().fit(sales)
    pred_test = final_forecaster.predict(template["Date"])
    anchor_test = forecaster_builders[anchor_scaled_key]().fit(sales).predict(template["Date"])
    submission = pred_test[["Date"] + TARGETS].copy()
    submission[TARGETS] = submission[TARGETS].clip(lower=0).round(2)
    submission["Date"] = template["Date"].dt.strftime("%Y-%m-%d").to_numpy()

    validate_submission(submission, template)

    out_file = output_dir / f"submission_train_forecasting_{PIPELINE_TAG}_guardrail.csv"
    try:
        submission.to_csv(out_file, index=False, encoding="utf-8-sig", lineterminator="\r\n")
    except PermissionError:
        out_file = output_dir / f"submission_train_forecasting_{PIPELINE_TAG}_guardrail_fallback.csv"
        submission.to_csv(out_file, index=False, encoding="utf-8-sig", lineterminator="\r\n")

    top_validation_rows = (
        metrics.head(8).astype(object).where(pd.notna(metrics.head(8)), None).to_dict(orient="records")
    )
    top_guardrail_rows = (
        guardrail_summary.head(12)
        .astype(object)
        .where(pd.notna(guardrail_summary.head(12)), None)
        .to_dict(orient="records")
    )
    test_mean_ratio_vs_v3 = {
        target: float(pred_test[target].mean() / anchor_test[target].mean()) for target in TARGETS
    }
    summary = {
        "validation_train_range": [
            train_valid["Date"].min().date().isoformat(),
            train_valid["Date"].max().date().isoformat(),
        ],
        "validation_range": [VALID_START.date().isoformat(), VALID_END.date().isoformat()],
        "final_train_range": [
            sales["Date"].min().date().isoformat(),
            sales["Date"].max().date().isoformat(),
        ],
        "best_model": best_model,
        "best_variant": best_variant,
        "metrics_file": str(metrics_file),
        "guardrail_metrics_file": str(guardrail_metrics_file),
        "guardrail_summary_file": str(guardrail_summary_file),
        "backtest_file": str(backtest_file),
        "submission_file": str(out_file),
        "test_mean_ratio_vs_v3": test_mean_ratio_vs_v3,
        "top_validation_rows": top_validation_rows,
        "top_guardrail_rows": top_guardrail_rows,
    }
    (project_root / f"forecast_{PIPELINE_TAG}_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8"
    )

    print("Validation split:")
    print(f"  train: {train_valid['Date'].min().date()} -> {train_valid['Date'].max().date()}")
    print(f"  valid: {valid['Date'].min().date()} -> {valid['Date'].max().date()}")
    print(f"Best pipeline: {best_model} / {best_variant}")
    print("Top validation metrics:")
    print(
        metrics[
            [
                "rank",
                "model",
                "variant",
                "target",
                "MAE",
                "RMSE",
                "R2",
                "valid_revenue_mean_ratio_vs_v3",
                "valid_cogs_mean_ratio_vs_v3",
            ]
        ]
        .head(8)
        .to_string(index=False)
    )
    print("Top guardrail metrics:")
    print(
        guardrail_summary[
            [
                "guardrail_rank",
                "model",
                "variant",
                "guardrail_avg_MAE_sum",
                "guardrail_worst_MAE_sum",
                "guardrail_avg_R2_mean",
            ]
        ]
        .head(12)
        .to_string(index=False)
    )
    print("Selected test mean ratio vs v3:")
    print(json.dumps(test_mean_ratio_vs_v3, indent=2))
    print(f"Saved metrics: {metrics_file}")
    print(f"Saved guardrail metrics: {guardrail_metrics_file}")
    print(f"Saved guardrail summary: {guardrail_summary_file}")
    print(f"Saved backtest: {backtest_file}")
    print(f"Saved submission: {out_file}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate on 2022, then refit 2012-2022 and forecast submission dates."
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="Project root containing dataset/sales.csv and dataset/sample_submission.csv.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_pipeline(args.project_root.resolve() if args.project_root else find_project_root())
