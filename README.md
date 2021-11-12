Raspberry Pi Torchscript Power/Runtime Evaluation Toolkit
===

![image](https://user-images.githubusercontent.com/5201073/141438280-44d40570-5e84-4ad9-bf40-39c2fc569061.png)

# Requirements
- Windows PC
- `Power-Z KM001` USB Power Consumption Monitor device
- Raspberry Pi

# Usage
1. (PC) Clone [jungin500/rpi-torchscript-eval-frontend](https://github.com/jungin500/rpi-torchscript-eval-frontend)
2. (PC) Change variables on `index.js` and run on native or build docker image with `Dockerfile`
3. (Raspberry Pi) Install this repository in `$RPI_EVAL_TOOLKIT_PATH` (Same path specified in `index.js` as `RPI_EVAL_TOOLKIT_PATH`)
4. (Raspberry Pi) Prepare conda environment which can `import torch` and load torchscript module
5. (PC) Open web browser and head to `http://$PC_IP_ADDRESS:8080/`. It will load frontend started while on Step 1~2.
