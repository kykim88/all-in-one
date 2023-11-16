import dataclasses
from dataclasses_avroschema import AvroModel #type:ignore
import datetime

@dataclasses.dataclass
class TestSchema(AvroModel):
    "Test Topic message"
    id : str
    value : float
    timestamp : datetime.datetime

    class Meta:
        schema_id = "https://my-schema-server/users/schema.avsc"