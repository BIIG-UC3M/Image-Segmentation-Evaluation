# Image Segmentation Evaluation
Evaluating segmentation algorithms using SimpleITK filters (Python) and results of statistical analysis (R) in order to demonstrate the statistical significance of comparisons between used models.

---
# Table of contents
- [Evaluation](#Evaluation)
    - [Preparing images for evaluation](#Preparing)
    - [Get Measures](#GetMeasures)
    - [Show Dataframe Stats](#ShowDataframeStats)
    - [Show GT](#ShowGT)
- [Statistical Analysis](#Analysis)

---


# Evaluation <a name="Evaluation"></a>
The python library can be found [here](./Evaluation.py).
## Preparing images for evaluation <a name="Preparing"></a>
In order to apply and evaluate segmentation models, images must be in a dictionary with the following structure:

```python 3
dict[Rater][Image] = [list_of_segmentations]
```
Where 
- _**Rater**_ is rater's ground truth name
- _**Image**_ is image's path
- _**list_of_segmentations**_ is the list of GT segmentations.

For example:

```python 3
data_dir = "/home/"
dataset_folders = sorted(glob.glob(os.path.join(data_dir,"subset*")))

images = []

segmentations = {"Rater_Name":{}}


for folder in dataset_folders:
    images = images + sorted(glob.glob(folder + "/*.mhd"))

for image in images:
        name = os.path.split(image)[1]
        segmentation_file_names = glob.glob(os.path.join(data_dir,'seg-lungs/',name))
        segmentations["Rater_Name"][image] = [segmentation_file_names]
```

## GetMeasures <a name="GetMeasures"></a>
Get Measures of applying Neural Network <model> to an image and its evaluation by SimpleITK filters. These measures will be saved in a csv file. Here is an example of how to apply this method. 
```python 3

rois_labels = {1:"Right_Lung", 2:"Left_Lung", 3:"Both_Lungs"}
GT_label_values = [2,3]
saving_path = "/path/results"
    
measures = GetMeasures(subset_name, segmentations, rois_labels, saving_path, GT_label_values = GT_label_values,
                       debug_mode = False, flip_image = True, flip_GT = True, image_extension = ".mhd", GT_extension = ".mhd")

```
Images and GTs must be in axial plane, as it is shown in the following pictures. If you need to rotate them, turn on flip_image and / or flip_GT. 

<img width="1066" alt="spacial location" src="https://user-images.githubusercontent.com/72487236/117801374-1d136100-b24c-11eb-9f1a-6428b96cdb11.png">
<img width="1066" alt="spacial location2" src="https://user-images.githubusercontent.com/72487236/117939847-61f8cf80-b300-11eb-8a4e-a14b9818c9b8.png">


## ShowDataframeStats <a name="ShowDataframeStats"></a>
This function makes a summary of the results obtained from applying the different models. It is neccesary to provide a common path where these results are located.


For example:

<pre>
                                dice                    
                                mean       max       min
Model           ROI                                     
mice_TL         Both_Lungs  0.243691  0.407057  0.140157
                Left_Lung   0.386391  0.575083  0.162955
                Right_Lung  0.087488  0.442705  0.000000
mix_No_TL       Both_Lungs  0.713815  0.959404  0.448105
mix_No_TL_A     Both_Lungs  0.342037  0.727465  0.038240
mix_No_TL_A_mac Both_Lungs  0.806413  0.968254  0.637035
mix_No_TL_mac   Both_Lungs  0.646839  0.951163  0.313299
mix_TL          Both_Lungs  0.897727  0.982022  0.638923
mix_TL_mac      Both_Lungs  0.893842  0.981281  0.636939
mix_TL_mic      Both_Lungs  0.897843  0.980992  0.636253


----------------------------------------------------------------------------
                                 mice_TL
----------------------------------------------------------------------------
------------------------------- Minimum Dice -------------------------------
                 Image    Model         ROI                  GT  dice
36  CTR_TRN_061.nii.gz  mice_TL  Right_Lung  CTR_TRN_061.nii.gz   0.0
39  CTR_TRN_061.nii.gz  mice_TL  Right_Lung   CTR_TRN_061_1.nii   0.0

------------------------------- Maximum Dice -------------------------------
                  Image    Model        ROI                  GT      dice
109  CTR_TRN_057.nii.gz  mice_TL  Left_Lung  CTR_TRN_057.nii.gz  0.575083
----------------------------------------------------------------------------



----------------------------------------------------------------------------
                                 mix_TL
----------------------------------------------------------------------------
------------------------------- Minimum Dice -------------------------------
                                    .
                                    .
                                    .
</pre>

## ShowGT <a name="ShowGT"></a>

This function show all GTs that are in the dictionary _segmentations_ and their labels. 

```python 3
ShowGT(segmentations,flip_GT)  
```
    
<img width="995" alt="showGT" src="https://user-images.githubusercontent.com/72487236/117799476-0e2baf00-b24a-11eb-9d1c-5c47b10c038a.png">

---
    
# Statistical Analysis <a name="Analysis"></a>
