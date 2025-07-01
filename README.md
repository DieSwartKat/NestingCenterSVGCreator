# NestingCenter SVG Creator

A Python library for converting Nesting Center data to SVG format with support for highlighting invalid geometry areas in red.

## Installation

```bash
pip install nestingcenter-svg
```

## Quick Start

```python
from nestingcenter_svg import NestingCenterSVGCreator

# Convert part data to SVG
svg_content = NestingCenterSVGCreator.createSvgPart(
    part_data, 
    geometryInvalid=invalid_curves  # Optional: highlight invalid areas in red
)

# Save to file
with open("output.svg", "w", encoding="utf-8") as file:
    file.write(svg_content)
```

## Features

- Convert Nesting Center part data to SVG format
- Support for various geometry types:
  - Rectangles
  - Contours (closed curves)
  - Polylines with bulge arcs
  - Elliptical arcs
  - NURBS curves
  - Circles and ellipses
- Highlight invalid geometry areas in red
- Proper viewBox calculation for optimal viewing
- Professional SVG output with proper namespaces

## Usage Example

```python
from nestingcenter_svg import NestingCenterSVGCreator

# Example with file conversion (assuming you have NestingConverters)
async def convert_dxf_to_svg():
    with open('input.dxf', mode='rb') as f:
        drawing_data = f.read()
    
    # Convert using your nesting service
    conversion_result = await NestingConverters.convert_part(session, drawing_data)
    
    # Create SVG
    svg = NestingCenterSVGCreator.createSvgPart(
        conversion_result['Parts'][0], 
        conversion_result.get('GeometryInvalid')
    )
    
    # Save result
    with open("output.svg", "w", encoding="utf-8") as file:
        file.write(svg)
```

## API Reference

### NestingCenterSVGCreator.createSvgPart(part, geometryInvalid=None)

Convert part data into SVG format.

**Parameters:**
- `part` (dict): Part data containing Box, Contours, etc.
- `geometryInvalid` (list, optional): List of invalid geometry curves to highlight in red

**Returns:**
- `str`: Complete SVG string ready for file output or web display

**Example part data structure:**
```python
part_data = {
    "Box": {
        "X1": 0.0,
        "Y1": 0.0,
        "X2": 100.0,
        "Y2": 50.0
    },
    "Contours": [
        {
            "Type": "Loop",
            "Data": {
                "Vertices": [
                    {"X": 0.0, "Y": 0.0},
                    {"X": 100.0, "Y": 0.0},
                    {"X": 100.0, "Y": 50.0},
                    {"X": 0.0, "Y": 50.0}
                ]
            }
        }
    ]
}
```

## Supported Geometry Types

The library supports various Nesting Center geometry types:

- **Rectangular shapes**: Simple rectangles with length and width
- **Contours**: Complex closed curves with multiple segments
- **Polylines**: Open curves with line segments and arcs
- **Elliptical arcs**: Partial ellipses with start/end angles
- **NURBS curves**: Non-uniform rational B-splines
- **Circles and ellipses**: Basic geometric shapes
- **Bulge arcs**: Arc segments defined by bulge factor

### Geometry Type Details

#### Loop/LoopBulge
Closed contours with vertices and optional bulge factors for arc segments.

#### Curve2CompositeClosed
Complex closed curves composed of multiple curve segments.

#### Circle2/Ellipse2
Basic geometric shapes with center and radius/axes information.

#### EllipticalArc2
Partial ellipses with start angle and sweep angle.

#### Nurbs2
NURBS (Non-Uniform Rational B-Spline) curves with control points and knot vectors.

## Requirements

- Python 3.7+
- geomdl>=5.0.0 (for NURBS curve support)

## Installation from Source

```bash
git clone https://github.com/DieSwartKat/NestingCenterSVGCreator.git
cd NestingCenterSVGCreator
pip install -e .
```

## Development

To set up for development:

```bash
git clone https://github.com/DieSwartKat/NestingCenterSVGCreator.git
cd NestingCenterSVGCreator
pip install -e .[dev]
```

### Development Tools

The project includes several development tools to maintain code quality:

**Testing:**
```bash
pytest                    # Run all tests
pytest -v                 # Run tests with verbose output
pytest --cov=nestingcenter_svg  # Run tests with coverage report
```

**Code Formatting:**
```bash
black .                   # Auto-format Python code to PEP 8 style
                         # Black is an opinionated code formatter that ensures consistent style
```

**Code Quality Checks:**
```bash
flake8                    # Check for style violations, unused imports, and potential errors
                         # Reports issues like long lines, unused variables, etc.
```

**Type Checking:**
```bash
mypy nestingcenter_svg    # Static type checking to catch type-related errors
                         # Validates type hints and catches potential runtime errors
```

### Development Tool Explanations

- **pytest**: Testing framework that runs your unit tests and reports results
- **black**: Code formatter that automatically formats your Python code to follow PEP 8 style guidelines consistently
- **flake8**: Linter that checks for programming errors, styling issues, and complexity problems
- **mypy**: Static type checker that analyzes your type hints to catch potential bugs before runtime

## Building and Publishing the Package

```bash
# Install build tools
pip install build twine

# Build the package (creates files in dist/ folder)
python -m build

# Check the built package for common issues
twine check dist/*

# Upload to PyPI (requires PyPI account and authentication)
twine upload dist/*

# For testing, upload to TestPyPI first
twine upload --repository testpypi dist/*
```

### Publishing Tool Explanations

- **build**: Creates distributable packages (wheel and source distribution) in the `dist/` folder
- **twine**: Securely uploads your package to PyPI (Python Package Index) so others can install it with `pip install`

## Error Handling

The library includes proper error handling for:
- Missing required dependencies (geomdl)
- Unsupported geometry types
- Invalid data structures
- Mathematical edge cases (division by zero, etc.)

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes and add tests
4. Run the development tools to ensure code quality:
   ```bash
   black .              # Format code
   flake8              # Check for issues
   mypy nestingcenter_svg  # Type check
   pytest              # Run tests
   ```
5. Commit your changes (`git commit -m 'Add some amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Author

**Martin Cronje**
- Email: martin.cronje.home@gmail.com
- GitHub: [@DieSwartKat](https://github.com/DieSwartKat)

## Changelog

### 0.1.0 (2024)
- Initial release
- Support for basic geometry types
- SVG output with proper viewBox
- Invalid geometry highlighting
- NURBS curve support
