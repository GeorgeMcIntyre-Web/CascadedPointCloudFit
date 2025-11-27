# External Test Data

This directory mirrors the **`Data_Clean`** bundle that ships with the original
CascadedPointCloudFit project.  Only the canonical `.ply` files are stored here
to keep the repository lean and avoid duplicate representations.

## Directory layout

```
test_data/external/
├── Clamp1.(csv|ply|txt)
├── Clamp2.(csv|ply|txt)
├── Slide1.(csv|ply)
├── Slide2.(csv|ply)
├── Clouds3/
├── Fails4/
├── IcpFails/
├── PinFails1/
└── PinFails2/
```

## Point cloud pairs

| Dataset      | Source (state A)                                     | Target (state B)                                     | Notes                                |
|--------------|------------------------------------------------------|------------------------------------------------------|--------------------------------------|
| Clamp        | `Clamp1.ply`                                         | `Clamp2.ply`                                         | Clean clamp mechanism reference      |
| Slide        | `Slide1.ply`                                         | `Slide2.ply`                                         | Large slide assembly (~170k points)  |
| Clouds3      | `Clouds3/016ZF-20137361-670B-109R_CI00_M2.ply`       | `Clouds3/016ZF-20137361-670B-109R_CI00_O2.ply`       | Medium difficulty                    |
| Fails4       | `Fails4/016ZF-20137361-670B-108_CI00_M1.ply`         | `Fails4/016ZF-20137361-670B-108_CI00_O1.ply`         | Historically challenging             |
| IcpFails (A) | `IcpFails/016ZF-20137361-670B-103R_CI00_M3.ply`      | `IcpFails/016ZF-20137361-670B-103R_CI00_O3.ply`      | Former ICP failure, now succeeds     |
| IcpFails (B) | `IcpFails/M.ply`                                     | `IcpFails/O.ply`                                     | Additional small-component pair      |
| PinFails1    | `PinFails1/016ZF-20137366-370-103-R_CI00_M.ply`      | `PinFails1/016ZF-20137366-370-103-R_CI00_O.ply`      | Pin mechanism, moderate difficulty   |
| PinFails2    | `PinFails2/file1.ply`                                | `PinFails2/file2.ply`                                | Alternate pin mechanism capture      |

> The `.txt` files provided with the clamp scenes contain simple metadata about
> capture settings and are optional.

## Usage

* **Python** – point readers automatically handle PLY.  CSV counterparts were
  removed here, but the original dataset still contains them if needed.
* **TypeScript** – the TypeScript implementation supports PLY via
  `PointCloudReader`.  You can point integration tests at `test_data/external`
  to validate new functionality or compare against the Python baseline.

## Attribution

The files originate from the upstream CascadedPointCloudFit dataset and are
redistributed here for internal testing purposes only.

