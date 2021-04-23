
import numpy as np
import torch
import SimpleITK as sitk
import myshow
import os
import glob
from caller import call
from importlib import reload
import pandas as pd
from IPython.display import clear_output
from collections import Counter


def ShowGT(segmentations,flip_GT):
    for rater in segmentations:
        print("  Rater: " + rater)
        for image_path in segmentations[rater]:  
            print("  Image: " + image_path)
            for segmentation in segmentations[rater][image_path]:
                segmentation = segmentation[0]
                GT = sitk.ReadImage(segmentation)
                
                if flip_GT:
                    GT = sitk.Flip(GT, [True,True,False])
                
                print("    GT Labels", np.unique(sitk.GetArrayFromImage(GT)))
                myshow.myshow(GT)

                
                
                
def GetMeasures(subset_name: str, segmentations: dict, rois_labels: dict, saving_path: str, GT_label_values = None,
                debug_mode = False, flip_image = False, flip_GT = False, image_extension = ".mhd", GT_extension = ".mhd", model = "human_org"):
    """
    Get Measures of applying Neural Network <call> to an image and its evaluation by 
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
    
    
    @return measures: List with above mentioned results. 
    """

    measures = []
    
    for rater in segmentations:
        for i, image_path in enumerate(segmentations[rater]):
            print('Image ' + str(i+1) + ' of ' + str(len(segmentations[rater])))
            print("  Image: " + image_path)
            
            image = ReadImage(image_path,image_extension)
            
            if len(os.path.split(image_path)[1]) > 0:    #Do not end with "/"
                image_name = os.path.split(image_path)[1]
            else:
                #image_name = os.path.split(os.path.split(image_path)[0])[1]   Cambiar
                image_name = os.path.split(os.path.split(image)[0])[1] + "/" + os.path.split(image)[1]
            if flip_image:
                image = sitk.Flip(image, [True,True,False])
                    
            auto_mask = call.apply(image,model) 
            
            for segmentation in segmentations[rater][image_path]:
                segmentation = segmentation[0]
                segmentation_name = os.path.split(segmentation)[1]
                print("  GT: " + segmentation)
            
                for label_key in rois_labels:
                    print("     ROI: " + rois_labels[label_key])
                    
                    GT = ReadImage(segmentation,GT_extension)
                    
                    if flip_GT:
                        GT = sitk.Flip(GT, [True,True,False])   
                    GT = sitk.GetArrayFromImage(GT)
                    
                    if len(GT.shape) == 4:
                        GT = GT[0,:,:,:]
                    
                    mask = np.copy(auto_mask)
                    
                    #Multiple Segmentations and only one GT_label_values
                    if GT_label_values != None:
                        try:
                            GT_label_values[s]
                            if isinstance(GT_label_values[s],list):

                                GT_labels = GT_label_values[s]
                            else:
                                GT_labels = GT_label_values
                        except:
                            GT_labels = GT_label_values
                    
                    elif GT_label_values == "FromFile":
                        GT_label_values = GetLabelFromFile(image_path,segmentation)
                    else:         
                        GT_labels = GetLungLabels(GT,debug_mode)
                    
                    mask, GT = ModifyLabels(mask,GT,label_key,rois_labels,GT_labels,flip_image, flip_GT)
                    seg = sitk.GetImageFromArray(mask)   
                    GT = sitk.GetImageFromArray(GT)
                    
                    
                    if debug_mode:
                        print()
                        print("    Auto Mask Labels", np.unique(sitk.GetArrayFromImage(seg)))
                        print("    There are " + str(np.sum(sitk.GetArrayFromImage(seg) != 0)) + " pixels in the auto mask different from zero")
                        myshow.myshow(seg)
                        print()
                        print()
                        print()
                        print()
                        
                        print()
                        print("    GT Labels", np.unique(sitk.GetArrayFromImage(GT)))
                        print("    There are " + str(np.sum(sitk.GetArrayFromImage(GT) != 0)) + " pixels in the GT different from zero")
                        myshow.myshow(GT)
                        print()
                        print()
                        print()
                        print()
                        
                        
                    
                    try:
                        seg.CopyInformation(GT)
                        overlap_measures_filter, hausdorff_distance_filter, all_surface_distances = CalcStatistics(seg,GT)
                        
                        jaccard_coefficient     = overlap_measures_filter.GetJaccardCoefficient()
                        dice_coefficient        = overlap_measures_filter.GetDiceCoefficient()
                        volume_similarity       = overlap_measures_filter.GetVolumeSimilarity()
                        false_negative          = overlap_measures_filter.GetFalseNegativeError()
                        false_positive          = overlap_measures_filter.GetFalsePositiveError()
                        
                        hausdorff_distance      = hausdorff_distance_filter.GetHausdorffDistance()
                        
                        mean_surface_distance   = np.mean(all_surface_distances)
                        median_surface_distance = np.median(all_surface_distances)
                        std_surface_distance    = np.std(all_surface_distances)
                        max_surface_distance    = np.max(all_surface_distances)
                        
                    except RuntimeError:
                        
                        jaccard_coefficient     = -1
                        dice_coefficient        = -1
                        volume_similarity       = -1
                        false_negative          = -1
                        false_positive          = -1
                        
                        hausdorff_distance      = -1
                        
                        mean_surface_distance   = -1
                        median_surface_distance = -1
                        std_surface_distance    = -1
                        max_surface_distance    = -1
                    
                    
                    measures.append({"Image":image_name, "Model": model, "Rater": rater, "ROI":rois_labels[label_key], "GT":segmentation_name,
                                     "jaccard":jaccard_coefficient, "dice":dice_coefficient, "vol_sim":volume_similarity, 
                                     "false_negative":false_negative,"false_positive":false_positive,
                                     "hausdorff_distance":hausdorff_distance,
                                     "mean_surface_distance":mean_surface_distance, "median_surface_distance":median_surface_distance,
                                     "std_surface_distance":std_surface_distance, "max_surface_distance":max_surface_distance})
                    
            if not(debug_mode):       
                clear_output()
    results_df = pd.DataFrame(measures)
    results_df.to_csv(r'' + saving_path + subset_name +'.csv', index = False, header=True)
    
    return measures

#####################################################################################################################################    
    
def ModifyLabels(auto_mask,GT,label_key,rois_labels,GT_label_values,flip_image, flip_GT):
    """ 
    Modify GT's labels values according to labels values from the mask generated by
    IA (i.e. right lung label is 1 and left lung label is 2). It is necessary to 
    provide a dictionary with these regions of interest (ROI), which it contains 
    label's name (e.g. "Left_Lung") and it is also mandatory to provide GT's original
    labels values. If it is provided a ROI name different from 
    [Right_Lung, Left_Lung or Both_Lungs], an exception will be raised.
    
    @param auto_mask: Mask generated by NN
    @param GT: Ground Truth Mask
    @param label_key: Label key for rois_labels
    @param rois_labels: Dictionary that contains labels' names.
    @param GT_label_values: Original GT's labels values
    
    @return auto_mask, GT: Modified masks so as to be compared 
    """
    
    if rois_labels[label_key] == 'Both_Lungs':
        if len(GT_label_values) == 2:
            GT[(GT != GT_label_values[0]) & (GT != GT_label_values[1])] = 0
            GT[(GT == GT_label_values[0]) | (GT == GT_label_values[1])] = 1
        else:
            GT[GT != GT_label_values[0]] = 0
            GT[GT == GT_label_values[0]] = 1
            
        auto_mask[auto_mask == 2] = 1
        
        
    elif rois_labels[label_key] == 'Left_Lung':
        if len(GT_label_values) == 2:
            if not flip_GT:
                GT[(GT != GT_label_values[0])] = 0
                GT[(GT == GT_label_values[0])] = 2
            else:
                GT[(GT != GT_label_values[0])] = 0
                GT[(GT == GT_label_values[0])] = 1
        else:
            if not flip_GT:
                GT[GT != GT_label_values[0]] = 0
                GT[GT == GT_label_values[0]] = 2
            else:
                GT[GT != GT_label_values[0]] = 0
                GT[GT == GT_label_values[0]] = 1
        
        if not flip_image:
            auto_mask[auto_mask == 1] = 0
        else:
            auto_mask[auto_mask == 2] = 0

        
    elif rois_labels[label_key] == 'Right_Lung':
        if len(GT_label_values) == 2:
            if not flip_GT:
                GT[(GT != GT_label_values[1])] = 0
                GT[(GT == GT_label_values[1])] = 1
            else:
                GT[(GT != GT_label_values[1])] = 0
                GT[(GT == GT_label_values[1])] = 2
        else:
            if not flip_GT:
                GT[GT != GT_label_values[1]] = 0
                GT[GT == GT_label_values[1]] = 1
            else:
                GT[GT != GT_label_values[1]] = 0
                GT[GT == GT_label_values[1]] = 2
                
        if not flip_image:        
            auto_mask[auto_mask == 2] = 0
        else:
            auto_mask[auto_mask == 1] = 0
        
    else:
        raise Exception('rois_labels can only be in [Right_Lung, Left_Lung and Both_Lungs]')
        
    GT = GT.astype(int)   
    return auto_mask, GT




def CalcStatistics(seg,GT):
    """ 
    Evaluate segmentation "seg" using ground truth "GT" by SimpleITK filters. The output
    are SimpleITK.LabelOverlapMeasuresImageFilter(), SimpleITK.HausdorffDistanceImageFilter() 
    and all_surface_distances.
    
      - SimpleITK.LabelOverlapMeasuresImageFilter() gives Dice Coefficient, Jaccard similarity 
      coefficient, Volume Similarity and False Negative and Flase Positive errors.
    
      - SimpleITK.HausdorffDistanceImageFilter() gives Hausdorff distance.
    
      - all_surface_distances gives Mean/Median/Std/Max Surface Distance and it is calculated
      by above filters.

    @param seg: Segmentation to be measured against
    @param GT: Ground Truth Mask
    
    @return overlap_measures_filter, hausdorff_distance_filter, all_surface_distances 
    """
   
    GT = sitk.Cast(GT, sitk.sitkUInt8)
    
    
    overlap_measures_filter = sitk.LabelOverlapMeasuresImageFilter()
    hausdorff_distance_filter = sitk.HausdorffDistanceImageFilter()
    
    reference_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(GT, squaredDistance=False, useImageSpacing=True))
    reference_surface = sitk.LabelContour(GT)

    statistics_image_filter = sitk.StatisticsImageFilter()
    # Get the number of pixels in the reference surface by counting all pixels that are 1.
    statistics_image_filter.Execute(reference_surface)
    num_reference_surface_pixels = int(statistics_image_filter.GetSum())
    
    # Overlap measures
    overlap_measures_filter.Execute(seg, GT)
        
    # Hausdorff distance
    hausdorff_distance_filter.Execute(seg, GT)
        
        
    # Symmetric surface distance measures
    segmented_distance_map = sitk.Abs(sitk.SignedMaurerDistanceMap(seg, squaredDistance=False, useImageSpacing=True))
    segmented_surface = sitk.LabelContour(seg)
        
    # Multiply the binary surface segmentations with the distance maps. The resulting distance
    # maps contain non-zero values only on the surface (they can also contain zero on the surface)
    seg2ref_distance_map = reference_distance_map*sitk.Cast(segmented_surface, sitk.sitkFloat32)
    ref2seg_distance_map = segmented_distance_map*sitk.Cast(reference_surface, sitk.sitkFloat32)
        
    # Get the number of pixels in the reference surface by counting all pixels that are 1.
    statistics_image_filter.Execute(segmented_surface)
    num_segmented_surface_pixels = int(statistics_image_filter.GetSum())
    
    # Get all non-zero distances and then add zero distances if required.
    seg2ref_distance_map_arr = sitk.GetArrayViewFromImage(seg2ref_distance_map)
    seg2ref_distances = list(seg2ref_distance_map_arr[seg2ref_distance_map_arr!=0]) 
    seg2ref_distances = seg2ref_distances + \
                        list(np.zeros(num_segmented_surface_pixels - len(seg2ref_distances)))
    ref2seg_distance_map_arr = sitk.GetArrayViewFromImage(ref2seg_distance_map)
    ref2seg_distances = list(ref2seg_distance_map_arr[ref2seg_distance_map_arr!=0]) 
    ref2seg_distances = ref2seg_distances + \
                        list(np.zeros(num_reference_surface_pixels - len(ref2seg_distances)))
        
    all_surface_distances = seg2ref_distances + ref2seg_distances
    
    return overlap_measures_filter, hausdorff_distance_filter, all_surface_distances       
    
    
    
def ReadImage(path : str, image_extension =".mhd"):
    
    def read_dicom(path):
        reader = sitk.ImageSeriesReader()
        dicom_names = reader.GetGDCMSeriesFileNames(path)
        reader.SetFileNames(dicom_names)
        return reader.Execute()
    
    
    if image_extension == ".mhd":
        image = sitk.ReadImage(path)
    elif image_extension == ".dcm":
        image = read_dicom(path)
    
    return image



def GetLungLabels(GT,debug_mode):

    z,y,x = GT.shape
    
    left = np.copy(GT[round(z/2),:,:])
    
    label_left_lung = Counter(left.flatten()).most_common(2)[1][0]
    

    right = np.copy(GT[round(z/2),:,:])
    right[:,round(y/2):y] = 0
    label_right_lung = Counter(right.flatten()).most_common(2)[1][0]

    
    if debug_mode:
        if label_left_lung == label_right_lung:
            print("    Original GT Labels [Both_Lungs]: [" + str(label_left_lung) + "]")
        else:
            print("    Original GT Labels [Left,Right]: [" + str(label_left_lung) + "," + str(label_right_lung) + "]")
    
    return [label_left_lung, label_right_lung]











def GetLabelFromFile(image_path,GT_path):
    
    image_name =  os.path.split(image_path)[1]
    GT_name = os.path.split(GT_path)[1]
    
    if image_path.find("nativeCTdata") != -1:
        if image_path.find("label_Organ.mhd") != -1:
            path = os.path.split(image_path)[0] + "Organ.cls"
        else:
            if image_name == "CT140.hdr":
                path = os.path.split(image_path)[0] + "Organ1.cls"
            elif image_name == "CT280.hdr":
                path = os.path.split(image_path)[0] + "Organ2.cls"
            
    elif image_path.find("enhancedCTdata") != -1:
        path = os.path.split(image_path)[0] + GT_name[6:-3] + "cls"
        
    
    def GetLabelValue(path, label = "Lung"):
        with open(path, 'r') as f:
            lines = f.readlines()
            l_values = lines[1][13:].split('|')
            l_names = lines[2][24:].split('|')
        
            indx = l_names.index(label)
        
        return l_values[indx]
    
    return GetLabelValue(path, label = "Lung")
