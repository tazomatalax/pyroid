from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Tuple, Optional


@dataclass
class GyroidParams:
    """Parameters for generating radially symmetrical gyroid structures."""
    res: int = field(default=80, metadata={"help": "Grid resolution in each dimension"})
    a: float = field(default=24.0, metadata={"help": "Dimension length along X-axis"})
    b: float = field(default=24.0, metadata={"help": "Dimension length along Y-axis"})
    c: float = field(default=10.0, metadata={"help": "Dimension length along Z-axis"})
    r1: float = field(default=12.0, metadata={"help": "Inner radius (central void size)"})
    r2: float = field(default=0.0, metadata={"help": "Outer radius"})
    phi_scale: float = field(default=8.0, metadata={"help": "Angular coordinate scaling factor (twists)"})
    wall_thickness: float = field(default=11.5, metadata={"help": "Wall thickness threshold"})
    cell_radius: float = field(default=2.0, metadata={"help": "Gyroid cell pore radius"})
    cell_height: float = field(default=3.0, metadata={"help": "Gyroid cell vertical height"})

    def validate(self) -> Tuple[bool, str]:
        """Validate parameter values for mathematical correctness."""
        if not isinstance(self.res, int) or self.res <= 0:
            return False, "Resolution must be a positive integer"
        if self.a <= 0 or self.b <= 0 or self.c <= 0:
            return False, "Dimensions (a, b, c) must be positive values"
        if self.r1 < 0:
            return False, "Inner radius (r1) must be non-negative"
        if self.wall_thickness <= 0:
            return False, "Wall thickness must be positive"
        if self.cell_radius <= 0 or self.cell_height <= 0:
            return False, "Cell radius and height must be positive"
        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert dataclass to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GyroidParams":
        """Instantiate GyroidParams from dictionary, filtering unknown fields."""
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: (int(v) if k == 'res' else float(v)) for k, v in data.items() if k in valid_keys}
        return cls(**filtered)


@dataclass
class STLConversionParams:
    """Parameters for converting an external STL file's volume into a gyroid lattice."""
    stl_path: str = field(metadata={"help": "Path to input STL file"})
    resolution: int = field(default=80, metadata={"help": "Voxel grid resolution along max dimension"})
    cell_size: float = field(default=5.0, metadata={"help": "Gyroid unit cell size (mm or model units)"})
    wall_thickness: float = field(default=0.5, metadata={"help": "Thickness of the gyroid lattice walls"})
    flat_cap: bool = field(default=True, metadata={"help": "Trim and cap top/bottom surfaces for 3D printing"})

    def validate(self) -> Tuple[bool, str]:
        if not self.stl_path:
            return False, "Input STL path must be specified"
        if self.resolution <= 10:
            return False, "Resolution must be at least 10"
        if self.cell_size <= 0:
            return False, "Cell size must be positive"
        if self.wall_thickness <= 0:
            return False, "Wall thickness must be positive"
        return True, ""
