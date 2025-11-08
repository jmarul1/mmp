# import pytest
# from stk_pred.entities.stocks import Stocks
# from stk_pred.ml.models.sequence import SequenceModel
# from stk_pred.pipeline.context import Context
# from stk_pred.pipeline.pipeline import Pipeline
# from stk_pred.pipeline.stages.collecting import PriceCollector
# from stk_pred.pipeline.stages.training import ClosePriceTrainer


# def test_pipeline_build(context_sample: Context):
#     pl = Pipeline(context_sample)
#     coll = PriceCollector()
#     trainer = ClosePriceTrainer(SequenceModel())
#     pl.add(coll, years_back=1)
#     pl.add(trainer)
#     assert pl.context.stock == context_sample.stock
#     assert len(pl) == 2
#     with pytest.raises(ValueError, match="Arguments passed are of the wrong type:"):
#         pl.add(123)
#     with pytest.raises(ValueError, match="Arguments passed are of the wrong type:"):
#         pl.add([123, 123])


# def test_pipeline_run(pipeline_sample: Pipeline) -> None:
#     ctx = pipeline_sample.context
#     pipeline_sample.execute()
#     assert ctx.stock.prices is not None
