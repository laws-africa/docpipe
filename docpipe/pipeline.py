import logging

log = logging.getLogger(__name__)


class PipelineContext:
    def __init__(self, pipeline):
        self.pipeline = pipeline


class Stage:
    name = None
    description = None

    def __init__(self, name=None, description=None):
        self.name = name or self.name or self.__class__.__name__
        self.description = description or self.description or self.__class__.__doc__

    def __call__(self, context):
        # must be implemented and modify items in the context
        pass


class Pipeline(Stage):
    """ A pipeline is a series of Stage objects that are called in order.

    A pipeline is itself a stage which allows nesting of pipelines.
    """
    def __init__(self, stages=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stages = stages or []

    def add(self, stage):
        self.stages.append(stage)

    def __call__(self, context):
        self.before(context)

        for stage in self.stages:
            self.before_stage(stage, context)
            stage(context)
            self.after_stage(stage, context)

        self.after(context)

    def before(self, context):
        pass

    def after(self, context):
        pass

    def before_stage(self, stage, context):
        pass

    def after_stage(self, stage, context):
        pass


class Attachment:
    """ An attachment object for stashing files to a document pipeline context.
    """
    def __init__(self, filename, content_type, file):
        self.filename = filename
        self.content_type = content_type
        self.file = file
