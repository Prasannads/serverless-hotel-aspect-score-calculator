import pandas as pd
from log import getLogger

LOG = getLogger(__name__)


class AggregateAspectScores:

    def __init__(self, df):
        self.df = df

    def aggregateScores(self):

        try:
            ## removing null scores
            self.df = self.df[self.df['score'].notnull()]

            ## normalizing the inconsistent scores
            self.df = self.df.join(pd.concat([self.df.groupby(['hotel_id', 'aspect'])[
                                   'score'].transform('min')], 1, keys=['min_score']))

            self.df = self.df.join(pd.concat([self.df.groupby(['hotel_id', 'aspect'])[
                                   'score'].transform('max')], 1, keys=['max_score']))

            self.df['normal_score'] = (
                self.df['score']-self.df['min_score'])/(self.df['max_score']-self.df['min_score'])

            grp_score = self.df.groupby(['hotel_id', 'aspect'])['score'].transform('last')

            self.df['normal_score'] = self.df['normal_score'].fillna(grp_score / 10000)

            # calculate the average score per aspect of a hotel
            self.df = self.df.groupby(['hotel_id', 'aspect'])[
                ['normal_score']].mean().reset_index()
            self.df.rename(columns={'normal_score': 'score'}, inplace=True)

            # rounding it off to make score between 0 and 100
            self.df.score = self.df['score'] * 100
            self.df.score = self.df['score'].round().astype('int64')

            return self.df
        except Exception as e:
            LOG.error("Error aggregating aspect scores " + str(e))
            raise Exception(str(e))
