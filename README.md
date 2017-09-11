# Project: Semantic Segmentation
*(Find the original readme in the second section)*

In this project, a model was developed to carry out semantic segmentation on images from a camera feed installed on a self-driving car. 

**Overview**: The [Kitti Road dataset](http://www.cvlibs.net/datasets/kitti/eval_road.php) was used as the training data. Following the approach in the [Fully Convolutional Networds for Semantic Segmentation](https://arxiv.org/pdf/1605.06211.pdf) paper, the final model consisted of an encoder part using the VGG pretrained model and a decoder part obtained by upsampling and skip layers to output same size as the input image.

**Augmentation:** I applied a brightness augmentation by converting image to HSV and then scaling up or down the V channel randomly with a factor of 0.3. This was implemented in the `gen_batch_function()` in helper.py. I also tried other augmentations like translation and flipping, which did not obtain a satisfactory result.
See a comparison between an augmented run and non-augmented run below.

[image1]: ./images/sem_seg.png "Comparison of results between an augmented run and non-augmented run below"
![alt text][image1]

We can observe that the result is more accurate with augmentation and there are lesser false positives in the augmented run.

The model was trained with a batch size of 2 and in 30 epochs. I applied the model on videos clips from previous projects. Result of application of model on video clips are shown here (from less difficult to more difficult scenes): [clip1](), [clip2](), [clip3](). 

**Conclusion:**
The result from this semantic segmentation project are satisfactory as the model can label most pixels of the road close to the best solution. In case of identifying only the road plane, the results here can be combined with an advanced lane finding pipeline to obtain more accurate road plane segmentation.


---
### Original readme follows:

# Semantic Segmentation

### Introduction
In this project, you'll label the pixels of a road in images using a Fully Convolutional Network (FCN).

### Setup
##### Frameworks and Packages
Make sure you have the following is installed:
 - [Python 3](https://www.python.org/)
 - [TensorFlow](https://www.tensorflow.org/)
 - [NumPy](http://www.numpy.org/)
 - [SciPy](https://www.scipy.org/)
##### Dataset
Download the [Kitti Road dataset](http://www.cvlibs.net/datasets/kitti/eval_road.php) from [here](http://www.cvlibs.net/download.php?file=data_road.zip).  Extract the dataset in the `data` folder.  This will create the folder `data_road` with all the training a test images.

### Start
##### Implement
Implement the code in the `main.py` module indicated by the "TODO" comments.
The comments indicated with "OPTIONAL" tag are not required to complete.
##### Run
Run the following command to run the project:
```
python main.py
```
**Note** If running this in Jupyter Notebook system messages, such as those regarding test status, may appear in the terminal rather than the notebook.

### Submission
1. Ensure you've passed all the unit tests.
2. Ensure you pass all points on [the rubric](https://review.udacity.com/#!/rubrics/989/view).
3. Submit the following in a zip file.
 - `helper.py`
 - `main.py`
 - `project_tests.py`
 - Newest inference images from `runs` folder
 
 ## How to write a README
A well written README file can enhance your project and portfolio.  Develop your abilities to create professional README files by completing [this free course](https://www.udacity.com/course/writing-readmes--ud777).
