import math
from typing import Dict, List, Optional, Any

try:
    from geomdl import BSpline
except ImportError:
    BSpline = None


class NestingCenterSVGCreator:
    """Create SVG from Nesting Center data."""

    @staticmethod
    def createSvgPart(
        part: Dict[str, Any], 
        geometryInvalid: Optional[List[Dict[str, Any]]] = None, 
        stroke_width: float = 1.0) -> str:
        """Convert a part data into svg part.
        
        Args:
            part: Part data dictionary containing Box, Contours, etc.
            geometryInvalid: Optional list of invalid geometry curves to highlight in red
            stroke_width: Line thickness for the SVG strokes (default: 1.0)
            
        Returns:
            Complete SVG string
        """
        box = part.get("Box", None)
        if box is not None:
            x1 = math.floor(part['Box']['X1']) - 1
            y1 = math.floor(part['Box']['Y1']) - 1
            vbWidth = math.ceil(part['Box']['X2']) - x1 + 2
            vbHeight = math.ceil(part['Box']['Y2']) - y1 + 2
        elif geometryInvalid and len(geometryInvalid) > 0:
            x1 = min(curve['Data']['ControlPoints'][0]['X'] for curve in geometryInvalid) - 10
            y1 = min(curve['Data']['ControlPoints'][0]['Y'] for curve in geometryInvalid) - 10
            x2 = max(curve['Data']['ControlPoints'][-1]['X'] for curve in geometryInvalid) + 10
            y2 = max(curve['Data']['ControlPoints'][-1]['Y'] for curve in geometryInvalid) + 10
            vbWidth = x2 - x1
            vbHeight = y2 - y1
        else:
            raise Exception("Part must have a Box or invalid geometry to determine SVG viewBox.")
        
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x1} {y1} {vbWidth} {vbHeight}" transform="scale(1 -1)" style="stroke:black;fill:none;stroke-width:{stroke_width}">'

        if part.get("RectangularShape") is not None:
            svg += NestingCenterSVGCreator.getSvgRectangle(part, False)
        else:
            for contour in part["Contours"]:
                path_data = NestingCenterSVGCreator.getSvgContour(contour, True)
                svg += f"<path d='{path_data}'/>"

            if geometryInvalid is not None:
                for curve in geometryInvalid:
                    path_data = NestingCenterSVGCreator.getSvgCurve(curve, True)
                    svg += f"<path d='{path_data}' stroke='red'/>"
        
        svg += '</svg>'
        return svg
    
    @staticmethod
    def getSvgArc(p1: Dict[str, Any], p2: Dict[str, Any]) -> str:
        bulge = p1['B']
        dx = p2['X'] - p1['X']
        dy = p2['Y'] - p1['Y']
        c = math.sqrt(dx * dx + dy * dy)
        s = c / 2 * bulge
        r = ((c * c / 4) + s * s) / (2 * s)
        sweep = 0 if bulge < 0 else 1
        large = 1 if math.fabs(bulge) > 1 else 0
        angle = math.atan2(dy, dx) * 180 / math.pi

        data = f" A {r},{r} {angle} {large},{sweep} {p2['X']} {p2['Y']}"
        return data
    
    @staticmethod
    def getSvgEllipticalArc(ellipse: Dict[str, Any], moveToStart: bool) -> str:
        ede = ellipse['Data']['Ellipse']
        cx = ede['Centre']['X']
        cy = ede['Centre']['Y']
        mx = ede['MajorAxis']['X']
        my = ede['MajorAxis']['Y']
        ratio = ede['Ratio']
        startAngle = ellipse['Data']['Range']['Start']
        sweepAngle = ellipse['Data']['Range']['Sweep']

        if sweepAngle >= 360:
            sweepAngle = 359.999

        sweep = 0 if sweepAngle < 0 else 1
        large = 1 if sweepAngle > 180 else 0
        r1 = math.sqrt(mx * mx + my * my)
        r2 = r1 * ratio

        startX = r1 * math.cos(startAngle * math.pi / 180.0)
        startY = r2 * math.sin(startAngle * math.pi / 180.0)
        endX = r1 * math.cos((startAngle + sweepAngle) * math.pi / 180.0)
        endY = r2 * math.sin((startAngle + sweepAngle) * math.pi / 180.0)

        angle = math.atan2(my, mx)
        angleDeg = angle * 180 / math.pi

        s = math.sin(angle)
        c = math.cos(angle)
        sX = startX * c - startY * s + cx
        sY = startX * s + startY * c + cy
        eX = endX * c - endY * s + cx
        eY = endX * s + endY * c + cy

        data = f"M {sX},{sY}" if moveToStart else ""
        data += f" A {r1},{r2} {angleDeg} {large},{sweep} {eX} {eY}"
        return data
    
    @staticmethod
    def getSvgCircle(circle: Dict[str, Any], moveToStart: bool) -> str:
        cx = circle['X']
        cy = circle['Y']
        r = circle['R']
        
        data = f"<circle cx='{cx}' cy='{cy}' r='{r}'/>" if moveToStart else f"<circle cx='{cx}' cy='{cy}' r='{r}'/>"
        return data

    @staticmethod
    def getSvgContour(contour: Dict[str, Any], move_to_start: bool) -> str:
        data = ""
        data_type = contour.get("Type")

        if data_type == "Curve2CompositeClosed":
            for curve_open in contour["Data"]["Chunks"]:
                data += NestingCenterSVGCreator.getSvgCurve(curve_open, move_to_start)
                move_to_start = (data == "")
            data += " Z"

        elif data_type in ("LoopBulge", "Loop"):
            data += NestingCenterSVGCreator.getSvgContourSimple(contour["Data"], move_to_start, True)

        elif data_type == "Circle2":
            data = NestingCenterSVGCreator.getSvgCircle(contour["Data"], move_to_start)

        elif data_type == "Ellipse2":
            data = NestingCenterSVGCreator.getSvgEllipse(contour["Data"], move_to_start)

        elif data_type is None:
            data += NestingCenterSVGCreator.getSvgContourSimple(contour, move_to_start, True)

        else:
            raise Exception("Unknown data type.")

        return data

    @staticmethod
    def getSvgContourSimple(contour: Dict[str, Any], move_to_start: bool, close_path: bool) -> str:
        vertices = contour["Vertices"]

        if len(vertices) < 2:
            return ""

        data = NestingCenterSVGCreator.getPos(vertices[0]) if move_to_start else ""

        for i in range(len(vertices)):
            prev_id = i - 1 if i > 0 else len(vertices) - 1
            prev_vertex = vertices[prev_id]
            curr_vertex = vertices[i]

            if "B" in prev_vertex:
                data += NestingCenterSVGCreator.getSvgArc(prev_vertex, curr_vertex)
            else:
                data += " L " + NestingCenterSVGCreator.getPos(curr_vertex)

        if "B" in vertices[-1]:
            data += NestingCenterSVGCreator.getSvgArc(vertices[-1], vertices[0])

        if close_path:
            data += " Z"

        if move_to_start:
            data = "M " + data

        return data

    @staticmethod
    def getSvgCurve(curve: Dict[str, Any], move_to_start: bool) -> str:
        data = ""
        data_type = curve.get("Type")

        if data_type == "Curve2CompositeOpen":
            for curve_chunk in curve["Data"]["Chunks"]:
                data += NestingCenterSVGCreator.getSvgCurve(curve_chunk, move_to_start)
                move_to_start = data == ""

        elif data_type in ("PolylineBulge", "Polyline"):
            data += NestingCenterSVGCreator.getSvgContourSimple(curve["Data"], move_to_start, close_path=False)

        elif data_type == "EllipticalArc2":
            data = NestingCenterSVGCreator.getSvgEllipticalArc(curve, move_to_start)

        elif data_type == "Nurbs2":
            data = NestingCenterSVGCreator.getSvgSpline(curve, move_to_start)

        else:
            raise Exception("Unknown data type.")

        return data

    @staticmethod
    def getSvgEllipse(ellipse: Dict[str, Any], moveToStart: bool) -> str:
        cx = ellipse['Centre']['X']
        cy = ellipse['Centre']['Y']
        ax = ellipse['MajorAxis']['X']
        ay = ellipse['MajorAxis']['Y']
        ratio = ellipse['Ratio']
        rx = 0
        ry = 0

        if ay == 0:
            rx = ax
            ry = ax * ratio
        elif ax == 0:
            rx = ay * ratio
            ry = ay
        else:
            raise Exception("Unsupported ellipse.")
        
        data = f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}'/>" if moveToStart else f"<ellipse cx='{cx}' cy='{cy}' rx='{rx}' ry='{ry}'/>"
        return data
    
    @staticmethod
    def getSvgRectangle(part: Dict[str, Any], winding_cw: bool) -> str:
        l = part["RectangularShape"]["Length"]
        w = part["RectangularShape"]["Width"]

        if winding_cw:
            points = f"0 0 0 {w} {l} {w} {l} 0 0 0"
        else:
            points = f"0 0 {l} 0 {l} {w} 0 {w} 0 0"

        svg = f"<polyline points='{points}'/>"
        return svg
    
    @staticmethod
    def getSvgSpline(spline: Dict[str, Any], moveToStart: bool) -> str:
        if BSpline is None:
            raise ImportError("geomdl package is required for spline support. Install with: pip install geomdl")
            
        controlPoints = spline['Data']['ControlPoints']
        cpCount = len(controlPoints)
        degree = len(spline['Data']['Knots']) - cpCount - 1

        if degree < 1:
            return ""

        data = f"M {controlPoints[0]['X']},{controlPoints[0]['Y']}" if moveToStart else ""
        
        if cpCount <= 4:
            data += " C"
            for i in range(1, 4):
                data += f" {controlPoints[i]['X']},{controlPoints[i]['Y']}"
        else:
            cp = [[pt['X'], pt['Y']] for pt in controlPoints]
            vertices = NestingCenterSVGCreator.getSplinePoints(cp, spline['Data']['Knots'], spline['Data']['Weights'], degree, 20)
            for i in range(1, len(vertices)):
                data += f" L {vertices[i][0]} {vertices[i][1]}"            
        
        return data

    @staticmethod   
    def getSplinePoints(cp: List[List[float]], knots: List[float], weights: Optional[List[float]], degree: int, n: int = 20) -> List[List[float]]:
        curve = BSpline.Curve()
        curve.degree = degree
        curve.ctrlpts = cp
        curve.knotvector = knots
        curve.weights = weights if weights else [1.0] * len(cp)
        curve_points = curve.evalpts
        return curve_points

    @staticmethod
    def getPos(pos: Dict[str, Any]) -> str:
        x = pos["X"]
        y = pos["Y"]
        return f"{x} {y}"