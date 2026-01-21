# Light Pollution Maps

This directory stores PNG light pollution maps used by the OptimalLocationFinder algorithm.

## Expected Map Format

- **File naming**: `RegionName2024.png` (e.g., `NorthAmerica2024.png`, `Europe2024.png`)
- **Color scale**: Grayscale or color-coded representing light pollution levels
- **Coverage**: Regional or global light pollution data

## Color Scale Mapping

The following RGB values map to light pollution levels:

| RGB Value       | Level | Description        |
|-----------------|-------|--------------------|
| (0, 0, 0)       | 0     | Darkest (best)     |
| (34, 34, 34)    | 1     | Very dark          |
| (61, 61, 61)    | 2     | Dark               |
| (85, 85, 85)    | 3     | Moderately dark    |
| (119, 119, 119) | 4     | Moderate           |
| (170, 170, 170) | 5     | Moderately bright  |
| (204, 204, 204) | 6     | Bright             |
| (255, 255, 255) | 7     | Brightest (worst)  |

## Data Sources

Light pollution maps can be obtained from:
- **Light Pollution Map**: https://www.lightpollutionmap.info/
- **Dark Site Finder**: https://darksitefinder.com/
- **Globe at Night**: https://www.globeatnight.org/

## Usage

Maps should be copied to this directory before using the OptimalLocationFinder.
The algorithm will automatically select the appropriate regional map based on coordinates.
