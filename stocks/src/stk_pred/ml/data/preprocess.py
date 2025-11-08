from pydantic import BaseModel


class Preprocess(BaseModel):
    def __call__(self, *args, **kwds):
        raise NotImplementedError("Subclasses must implement this method")
