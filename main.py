from nestingcenter_svg import NestingCenterSVGCreator

data = NestingCenterSVGCreator.createEmptyGeometrySvg(200, 100)
print(data)


with open("empty_geometry.svg", "w") as f:
    f.write(data)