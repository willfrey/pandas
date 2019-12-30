import numpy as np
import pytest

from pandas import DataFrame, Series
import pandas.util.testing as tm


class TestDataFramePctChange:
    def test_pct_change_numeric(self):
        # GH#11150
        pnl = DataFrame(
            [np.arange(0, 40, 10), np.arange(0, 40, 10), np.arange(0, 40, 10)]
        ).astype(np.float64)
        pnl.iat[1, 0] = np.nan
        pnl.iat[1, 1] = np.nan
        pnl.iat[2, 3] = 60

        for axis in range(2):
            expected = pnl.ffill(axis=axis) / pnl.ffill(axis=axis).shift(axis=axis) - 1
            result = pnl.pct_change(axis=axis, fill_method="pad")

            tm.assert_frame_equal(result, expected)

    def test_pct_change(self, datetime_frame):
        rs = datetime_frame.pct_change(fill_method=None)
        tm.assert_frame_equal(rs, datetime_frame / datetime_frame.shift(1) - 1)

        rs = datetime_frame.pct_change(2)
        filled = datetime_frame.fillna(method="pad")
        tm.assert_frame_equal(rs, filled / filled.shift(2) - 1)

        rs = datetime_frame.pct_change(fill_method="bfill", limit=1)
        filled = datetime_frame.fillna(method="bfill", limit=1)
        tm.assert_frame_equal(rs, filled / filled.shift(1) - 1)

        rs = datetime_frame.pct_change(freq="5D")
        filled = datetime_frame.fillna(method="pad")
        tm.assert_frame_equal(
            rs, (filled / filled.shift(freq="5D") - 1).reindex_like(filled)
        )

    def test_pct_change_shift_over_nas(self):
        s = Series([1.0, 1.5, np.nan, 2.5, 3.0])

        df = DataFrame({"a": s, "b": s})

        chg = df.pct_change()
        expected = Series([np.nan, 0.5, 0.0, 2.5 / 1.5 - 1, 0.2])
        edf = DataFrame({"a": expected, "b": expected})
        tm.assert_frame_equal(chg, edf)

    @pytest.mark.parametrize(
        "freq, periods, fill_method, limit",
        [
            ("5B", 5, None, None),
            ("3B", 3, None, None),
            ("3B", 3, "bfill", None),
            ("7B", 7, "pad", 1),
            ("7B", 7, "bfill", 3),
            ("14B", 14, None, None),
        ],
    )
    def test_pct_change_periods_freq(
        self, datetime_frame, freq, periods, fill_method, limit
    ):
        # GH#7292
        rs_freq = datetime_frame.pct_change(
            freq=freq, fill_method=fill_method, limit=limit
        )
        rs_periods = datetime_frame.pct_change(
            periods, fill_method=fill_method, limit=limit
        )
        tm.assert_frame_equal(rs_freq, rs_periods)

        empty_ts = DataFrame(index=datetime_frame.index, columns=datetime_frame.columns)
        rs_freq = empty_ts.pct_change(freq=freq, fill_method=fill_method, limit=limit)
        rs_periods = empty_ts.pct_change(periods, fill_method=fill_method, limit=limit)
        tm.assert_frame_equal(rs_freq, rs_periods)