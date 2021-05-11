# Image Segmentation-Evaluation
Evaluating segmentation algorithms using SimpleITK filters

## Preparing images for evaluation
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

## GetMeasures

```python 3
GetMeasures(subset_name: str, segmentations: dict, rois_labels: dict, saving_path: str, 
            GT_label_values = None, debug_mode = False, flip_image = False, flip_GT = False,
            image_extension = ".mhd", GT_extension = ".mhd", model = "human_org"):
    """
    Get Measures of applying Neural Network <model> to an image and its evaluation by 
    SimpleITK filters (if you desired to know more about measures, 
    type <help(CalcStatistics)>). These measures will be stored in a list and then saved
    in a csv file. This csv file will be created at saving_path.
    
    @param subset_name: Desired name for the csv file.
    
    @param segmentations: It is a dictionary with the following structure: 
                          segmentations = {Rater,{Image,GT_paths[]}}
                          *Important* Even if there is only one GT path, it
                          must be a list. 
                          
    @param rois_labels: It is a dictionary with the following structure: 
                          rois_labels = {Key:"ROI_Label"}
                          ROI_Label must be in ["Right_Lung", "Left_Lung","Both_Lungs"]
                          
    @param saving_path: Path where the csv will be saved.
    
    
    
    Optional parameters:
        @param GT_label_values: Original GT's labels values. They must be provided in this
                                way: [Left Lung,Right Lung]. If they are not provided,
                                they will be obtained automatically from the GT mask.
    
        @param debug_mode: Set it <True> to activate debug mode.
        
        @param flip_image: Set it <True> to flip images.
        
        @param flip_GT: Set it <True> to flip GT masks.
        
        @param image_extension: Default value is ".mhd". Accepted extensions are 
                                ".mhd" and ".dcm".
                                
        @param GT_extension: Default value is ".mhd". Accepted extensions are 
                                ".mhd" and ".dcm".
        
        @param model: Default value is "human_org".
    
    
    @return measures: List with above mentioned results. 
    """
```
Images and GTs must have the following spacial location. If not, turn on flip_image and / or flip_GT. 

<img width="1066" alt="spacial location" src="https://user-images.githubusercontent.com/72487236/117801374-1d136100-b24c-11eb-9f1a-6428b96cdb11.png">

## ShowDataframeStats
ShowDataframeStats(path). This function makes a summary of the results obtained from applying the different models. It is neccesary to provide a common path where these results are located.


For example

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
<pre>

## ShowGT
ShowGT(segmentations, flip_GT). This function show all GTs that are in <segmentations>. 
<img width="995" alt="showGT" src="https://user-images.githubusercontent.com/72487236/117799476-0e2baf00-b24a-11eb-9d1c-5c47b10c038a.png">

