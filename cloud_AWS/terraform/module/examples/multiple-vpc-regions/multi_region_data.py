import configparser
from dataclasses import dataclass, fields
from typing import Any, Dict, List, Type, TypeVar


MultiRegionDataType = TypeVar("MultiRegionDataType", bound="MultiRegionData")


@dataclass
class MultiRegionData:
    external_id: str = ""
    plan_id: str = ""
    region: str = ""
    s3_bucket_prefix: str = ""

    @classmethod
    def from_dict(cls: Type[MultiRegionDataType], data: Dict[str, Any]) -> MultiRegionDataType:
        for k in [f.name for f in fields(cls) if f.type == List[str] and f.name in data]:
            data[k] = [name.strip() for name in data[k].split(",") if name]

        return cls(**data)


def load_multi_region_data(file_path: str) -> List[MultiRegionData]:
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
    except configparser.Error as err:
        raise Exception(f"Failed to load '{file_path}'") from err
    return [MultiRegionData.from_dict(dict(v)) for k, v in config.items() if k != "DEFAULT"]

