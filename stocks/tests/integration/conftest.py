# import pytest
# from stk_pred.entities.stock import Stock
# from stk_pred.entities.stocks import Stocks
# from stk_pred.pipeline.context import Context
# from stk_pred.pipeline.pipeline import Pipeline
# from stk_pred.pipeline.stages.collecting import PriceCollector


# @pytest.fixture
# def context_sample() -> Context:
#     return Context(Stock("AAPL", "Apple"))


# @pytest.fixture
# def pipeline_sample(context_sample: Stock) -> Pipeline:  # pylint: disable = redefined-outer-name
#     pl = Pipeline(context_sample)
#     coll = PriceCollector()
#     pl.add(coll, years_back=0.01)
#     return pl
