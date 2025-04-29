from typing import Any, Dict, List, Optional, Set, Tuple, Union, TypeVar, ClassVar, Type, overload
import numpy as np
from numpy.typing import NDArray
import os
import pickle
import json

T = TypeVar('T')

class data_cubby:
    cubby: ClassVar[Dict[str, Any]]
    class_registry: ClassVar[Dict[str, Any]]
    subclass_registry: ClassVar[Dict[str, Any]]
    use_pkl_storage: ClassVar[bool]
    base_pkl_directory: ClassVar[Optional[str]]
    
    @classmethod
    def set_storage_directory(cls, directory: str) -> None: ...
    
    @classmethod
    def _get_storage_path_for_object(cls, obj: Any) -> str: ...
    
    @classmethod
    def save_to_disk(cls) -> bool: ...
    
    @classmethod
    def load_from_disk(cls) -> bool: ...
    
    @classmethod
    def stash(cls, obj: T, class_name: Optional[str] = None, subclass_name: Optional[str] = None) -> T: ...
    
    @classmethod
    def grab(cls, identifier: str) -> Any: ...
    
    @classmethod
    def get_all_keys(cls) -> Dict[str, List[str]]: ...
    
    @classmethod
    def grab_component(cls, class_name: str, subclass_name: str) -> Any: ...
    
    @classmethod
    def make_globally_accessible(cls, name: str, variable: Any) -> Any: ...

class Variable:
    class_name: str
    subclass_name: str
    datetime_array: Optional[NDArray]
    time_values: Optional[NDArray]
    values: Optional[NDArray]
    data_type: Optional[str]
    internal_id: int
    
    def __init__(self, class_name: str, subclass_name: str) -> None: ...
    
    def __array__(self) -> NDArray: ...
    
    def __len__(self) -> int: ...
    
    def __getitem__(self, key: Union[int, slice]) -> Any: ...
    
    def __repr__(self) -> str: ...

# Global instance
data_cubby: data_cubby
