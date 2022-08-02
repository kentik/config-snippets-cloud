import configparser
from dataclasses import dataclass, field
from typing import List


@dataclass
class RegionData:
    aws_region_name: str = ""
    s3_bucket_prefix: str = ""


@dataclass
class MultiRegionData:
    external_id: str = ""
    plan_id: str = ""
    regions: List[RegionData] = field(default_factory=list)


def load_multi_region_data(file_path: str) -> MultiRegionData:
    config = configparser.ConfigParser()
    try:
        config.read(file_path)
        external_id = config["DEFAULT"]["external_id"]
        plan_id = config["DEFAULT"]["plan_id"]
        regions = [
            RegionData(aws_region_name=v["region"], s3_bucket_prefix=v.get("s3_bucket_prefix", ""))
            for k, v in config.items()
            if k != "DEFAULT"
        ]
    except (KeyError, configparser.Error) as err:
        raise Exception(f"Failed to load '{file_path}'") from err

    return MultiRegionData(external_id=external_id, plan_id=plan_id, regions=regions)
