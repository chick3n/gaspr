import dataclasses
from gaspr.persistent.models import File

@dataclasses.dataclass
class LlamaIndexResponse():
    text: str = None

@dataclasses.dataclass
class LlamaIndexRefresh():
    updated: list[File] = dataclasses.field(default_factory=list)
    added: list[File] = dataclasses.field(default_factory=list)