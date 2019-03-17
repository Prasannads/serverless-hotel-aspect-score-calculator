from aggregate_aspect_scores import AggregateAspectScores
from tests import *
import pandas as pd
from pandas.util.testing import assert_frame_equal
import pytest


@pytest.fixture
def aggregate_aspect_score():
    input_data = [[872840866, 'cleanliness', 'source_A', 7050],
                  [872840866, 'cleanliness', 'source_C', ],
                  [872840866, 'value_for_money', 'source_C', 8190]]
    input_df = pd.DataFrame(input_data, columns=[
                            'hotel_id', 'aspect', 'source', 'score'])
    actual_df = AggregateAspectScores(input_df).aggregateScores()
    return actual_df


def test_agg_aspect_scores(aggregate_aspect_score):
        expected_data = [[872840866, 'cleanliness', 70],
                         [872840866, 'value_for_money', 82]]
        expected_df = pd.DataFrame(expected_data, columns=[
                                   'hotel_id', 'aspect', 'score'])
        assert_frame_equal(expected_df, aggregate_aspect_score)


def test_scores_should_not_be_null(aggregate_aspect_score):
        expected_list = []
        aggregate_aspect_score = aggregate_aspect_score[aggregate_aspect_score['score'].isnull(
        )]
        actual_list = aggregate_aspect_score['score'].tolist()
        assert expected_list == actual_list


def test_scores_should_be_between_0_and_100(aggregate_aspect_score):
        min_score, max_score = aggregate_aspect_score['score'].min(
        ), aggregate_aspect_score['score'].max()
        expected_min_score, expected_max_score = 0, 100
        assert min_score >= expected_min_score and max_score <= expected_max_score
