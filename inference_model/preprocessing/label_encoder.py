from typing import List, Optional

import pandas as pd
from sklearn.exceptions import NotFittedError


class LabelEncoder(object):
    r"""Label Encode categorical values for multiple columns at once

    :information_source: **NOTE**:
    Shamlessly copied from https://github.com/jrzaurin/pytorch-widedeep

    :information_source: **NOTE**:
    LabelEncoder reserves 0 for `unseen` new categories. This is convenient
    when defining the embedding layers, since we can just set padding idx to 0.

    Parameters:
        columns_to_encode (list, Optional, default = None): List of strings containing
            the names of the columns to encode. If `None` all columns of type `object`
            in the dataframe will be label encoded.

    Attributes:
        encoding_dict (Dict): Dictionary containing the encoding mappings in the format,
            e.g. : <br/> `{'colname1': {'cat1': 1, 'cat2': 2, ...}, 'colname2': {'cat1': 1, 'cat2': 2, ...}, ...}`  # noqa
        inverse_encoding_dict(Dict): Dictionary containing the inverse encoding mappings
            in the format, e.g. : <br/> `{'colname1': {1: 'cat1', 2: 'cat2', ...}, 'colname2': {1: 'cat1', 2: 'cat2', ...}, ...}`  # noqa
    """

    def __init__(
        self,
        columns_to_encode: Optional[List[str]] = None,
    ):
        self.columns_to_encode = columns_to_encode

    def fit(self, df: pd.DataFrame) -> "LabelEncoder":
        """Creates encoding attributes

        Returns:
            LabelEncoder: `LabelEncoder` fitted object
        """

        df_inp = df.copy()

        if self.columns_to_encode is None:
            self.columns_to_encode = list(
                df_inp.select_dtypes(include=["object"]).columns
            )
        else:
            # sanity check to make sure all categorical columns are in an adequate
            # format
            for col in self.columns_to_encode:
                df_inp[col] = df_inp[col].astype("O")

        unique_column_vals = dict()
        for c in self.columns_to_encode:
            unique_column_vals[c] = df_inp[c].unique()

        self.encoding_dict = dict()

        # leave 0 for padding/"unseen" categories
        idx = 1
        for k, v in unique_column_vals.items():
            self.encoding_dict[k] = {
                o: i + idx for i, o in enumerate(unique_column_vals[k])
            }
            idx = 1

        self.inverse_encoding_dict = dict()
        for c in self.encoding_dict:
            self.inverse_encoding_dict[c] = {
                v: k for k, v in self.encoding_dict[c].items()
            }
            self.inverse_encoding_dict[c][0] = "unseen"

        return self

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Label Encoded the categories in `columns_to_encode`

        Returns:
            pd.DataFrame: label-encoded dataframe
        """
        try:
            self.encoding_dict
        except AttributeError:
            raise NotFittedError(
                "This LabelEncoder instance is not fitted yet. "
                "Call 'fit' with appropriate arguments before using this LabelEncoder."
            )

        df_inp = df.copy()
        # sanity check to make sure all categorical columns are in an adequate
        # format
        for col in self.columns_to_encode:  # type: ignore
            df_inp[col] = df_inp[col].astype("O")

        for k, v in self.encoding_dict.items():
            df_inp[k] = df_inp[k].apply(lambda x: v[x] if x in v.keys() else 0)

        return df_inp

    def fit_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Combines `fit` and `transform`

        Returns:
            pd.DataFrame: label-encoded dataframe

        Examples:
            >>> import pandas as pd
            >>> from data_preparation.label_encoder import LabelEncoder
            >>> df = pd.DataFrame({'col1': [1,2,3], 'col2': ['me', 'you', 'him']})
            >>> columns_to_encode = ['col2']
            >>> encoder = LabelEncoder(columns_to_encode)
            >>> encoder.fit_transform(df)
               col1  col2
            0     1     1
            1     2     2
            2     3     3
            >>> encoder.encoding_dict
            {'col2': {'me': 1, 'you': 2, 'him': 3}}
        """
        return self.fit(df).transform(df)

    def inverse_transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Returns the original categories

        Returns:
            pd.DataFrame: label-encoded dataframe

        Examples:
            >>> import pandas as pd
            >>> from data_preparation.label_encoder import LabelEncoder
            >>> df = pd.DataFrame({'col1': [1,2,3], 'col2': ['me', 'you', 'him']})
            >>> columns_to_encode = ['col2']
            >>> encoder = LabelEncoder(columns_to_encode)
            >>> df_enc = encoder.fit_transform(df)
            >>> encoder.inverse_transform(df_enc)
               col1 col2
            0     1   me
            1     2  you
            2     3  him
        """
        for k, v in self.inverse_encoding_dict.items():
            df[k] = df[k].apply(lambda x: v[x])
        return df
