# Unit test _extract_data_folds_multiseries
# ==============================================================================
import re
import pytest
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
from skforecast.exceptions import IgnoredArgumentWarning
from skforecast.ForecasterAutoreg import ForecasterAutoreg
from skforecast.ForecasterAutoregMultiSeries import ForecasterAutoregMultiSeries
from skforecast.ForecasterAutoregMultiSeriesCustom import ForecasterAutoregMultiSeriesCustom
from skforecast.ForecasterAutoregMultiVariate import ForecasterAutoregMultiVariate
from skforecast.model_selection_multiseries.model_selection_multiseries import _extract_data_folds_multiseries

# Fixtures
series = pd.DataFrame({
    'l1': np.arange(50, dtype=float),
    'l2': np.arange(50, 100, dtype=float),
    'l3': np.arange(100, 150, dtype=float)
})
exog = pd.DataFrame({
    'exog_1': np.arange(1000, 1050, dtype=float),
    'exog_2': np.arange(1050, 1100, dtype=float),
    'exog_3': np.arange(1100, 1150, dtype=float)
})


@pytest.mark.parametrize("dropna_last_window", 
                         [True, False], 
                         ids=lambda dropna: f'dropna_last_window: {dropna}')
def test_extract_data_folds_multiseries_series_DataFrame_exog_None_RangeIndex(dropna_last_window):
    """
    Test extract_data_folds_multiseries with series DataFrame and exog None.
    """

    # Train, last_window, test_no_gap
    folds = [
        [[0, 30], [25, 30], [30, 37]], 
        [[0, 35], [30, 35], [35, 42]]
    ]
    span_index = pd.RangeIndex(start=0, stop=50, step=1)
    window_size = 5

    data_folds = list(
        _extract_data_folds_multiseries(
            series             = series, 
            folds              = folds, 
            span_index         = span_index, 
            window_size        = window_size, 
            exog               = None, 
            dropna_last_window = dropna_last_window, 
            externally_fitted  = False
        )
    )

    expected_data_folds = [
        (
            pd.DataFrame(
                data = {'l1': np.arange(0, 30, dtype=float),
                        'l2': np.arange(50, 80, dtype=float),
                        'l3': np.arange(100, 130, dtype=float)
                },
                index = pd.RangeIndex(start=0, stop=30, step=1)
            ), 
            pd.DataFrame(
                data = {'l1': np.arange(25, 30, dtype=float),
                        'l2': np.arange(75, 80, dtype=float),
                        'l3': np.arange(125, 130, dtype=float)
                },
                index = pd.RangeIndex(start=25, stop=30, step=1)
            ),
            ['l1', 'l2', 'l3'],
            None, 
            None, 
            folds[0]
        ),
        (
            pd.DataFrame(
                data = {'l1': np.arange(0, 35, dtype=float),
                        'l2': np.arange(50, 85, dtype=float),
                        'l3': np.arange(100, 135, dtype=float)
                },
                index = pd.RangeIndex(start=0, stop=35, step=1)
            ), 
            pd.DataFrame(
                data = {'l1': np.arange(30, 35, dtype=float),
                        'l2': np.arange(80, 85, dtype=float),
                        'l3': np.arange(130, 135, dtype=float)
                },
                index = pd.RangeIndex(start=30, stop=35, step=1)
            ),
            ['l1', 'l2', 'l3'],
            None,
            None,
            folds[1]
        )
    ]

    for i, data_fold in enumerate(data_folds):

        assert isinstance(data_fold, tuple)
        assert len(data_fold) == 6
        
        pd.testing.assert_frame_equal(data_fold[0], expected_data_folds[i][0])
        pd.testing.assert_frame_equal(data_fold[1], expected_data_folds[i][1])
        assert data_fold[2] == expected_data_folds[i][2]
        assert data_fold[3] is None
        assert data_fold[4] is None
        assert data_fold[5] == expected_data_folds[i][5]


@pytest.mark.parametrize("dropna_last_window", 
                         [True, False], 
                         ids=lambda dropna: f'dropna_last_window: {dropna}')
def test_extract_data_folds_multiseries_series_DataFrame_with_NaN_exog_RangeIndex(dropna_last_window):
    """
    Test extract_data_folds_multiseries with series DataFrame and exog None.
    """
    series_nan = series.copy()
    series_nan.loc[:28, 'l2'] = np.nan
    series_nan['l3'] = np.nan

    # Train, last_window, test_no_gap
    folds = [
        [[0, 30], [25, 30], [30, 37]], 
        [[0, 35], [30, 35], [35, 42]]
    ]
    span_index = pd.RangeIndex(start=0, stop=50, step=1)
    window_size = 5

    data_folds = list(
        _extract_data_folds_multiseries(
            series             = series_nan, 
            folds              = folds, 
            span_index         = span_index, 
            window_size        = window_size, 
            exog               = exog, 
            dropna_last_window = dropna_last_window, 
            externally_fitted  = False
        )
    )

    expected_data_folds = [
        (
            pd.DataFrame(
                data = {'l1': np.arange(0, 30, dtype=float)
                },
                index = pd.RangeIndex(start=0, stop=30, step=1)
            ),
            pd.DataFrame(
                data = {'l1': np.arange(25, 30, dtype=float)
                },
                index = pd.RangeIndex(start=25, stop=30, step=1)
            ),
            ['l1'],
            pd.DataFrame(
                data = {'exog_1': np.arange(1000, 1030, dtype=float),
                        'exog_2': np.arange(1050, 1080, dtype=float),
                        'exog_3': np.arange(1100, 1130, dtype=float)
                },
                index = pd.RangeIndex(start=0, stop=30, step=1)
            ),
            pd.DataFrame(
                data = {'exog_1': np.arange(1030, 1037, dtype=float),
                        'exog_2': np.arange(1080, 1087, dtype=float),
                        'exog_3': np.arange(1130, 1137, dtype=float)
                },
                index = pd.RangeIndex(start=30, stop=37, step=1)
            ),
            folds[0]
        ),
        (
            pd.DataFrame(
                data = {'l1': np.arange(0, 35, dtype=float),
                        'l2': [np.nan]*29 + list(range(79, 85))
                },
                index = pd.RangeIndex(start=0, stop=35, step=1)
            ).astype({'l2': float}), 
            pd.DataFrame(
                data = {'l1': np.arange(30, 35, dtype=float),
                        'l2': np.arange(80, 85, dtype=float)
                },
                index = pd.RangeIndex(start=30, stop=35, step=1)
            ),
            ['l1', 'l2'],
            pd.DataFrame(
                data = {'exog_1': np.arange(1000, 1035, dtype=float),
                        'exog_2': np.arange(1050, 1085, dtype=float),
                        'exog_3': np.arange(1100, 1135, dtype=float)
                },
                index = pd.RangeIndex(start=0, stop=35, step=1)
            ),
            pd.DataFrame(
                data = {'exog_1': np.arange(1035, 1042, dtype=float),
                        'exog_2': np.arange(1085, 1092, dtype=float),
                        'exog_3': np.arange(1135, 1142, dtype=float)
                },
                index = pd.RangeIndex(start=35, stop=42, step=1)
            ),
            folds[1]
        )
    ]

    for i, data_fold in enumerate(data_folds):

        assert isinstance(data_fold, tuple)
        assert len(data_fold) == 6
        
        pd.testing.assert_frame_equal(data_fold[0], expected_data_folds[i][0])
        pd.testing.assert_frame_equal(data_fold[1], expected_data_folds[i][1])
        assert data_fold[2] == expected_data_folds[i][2]
        pd.testing.assert_frame_equal(data_fold[3], expected_data_folds[i][3])
        pd.testing.assert_frame_equal(data_fold[4], expected_data_folds[i][4])
        assert data_fold[5] == expected_data_folds[i][5]

