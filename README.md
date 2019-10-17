# GeyserWatch
Predicting geyser eruptions at Yellowstone National Park

www.geyserwatch.xyz

**Background and Motivation**

4 Million visitors come to the Yellowstone National Park annually to experience the unique geo-thermal activity of the area, and witness the spectacular geyser eruptions. They rely on the predictions provided by the National Park Service (NPS) to plan their day, however the NPS prediction windows can often range from	±45 minutes to ±2 hours making it impractical for visitors to plan their day around this level of uncertainty. I was interested to see if these prediction windows could be improved upon.

**Accessing Data and EDA**

I acccessed historical data from the archives of Geyser Times : https://geysertimes.org/archive/ . Geyser Times provides free access to historical geyser eruption data that is updated nightly.

Because the data dump tsv file is large in size (~120mb), it has not been included in this github repo. However it can be downloaded from the link above.

After a bit of data cleaning, preliminary EDA revealed various aspects of the data. The python notebook data_Cleanup_EDA.ipynb contains the relevant steps as well as a couple of EDA plots. From the plots its clear that the data is irregularly spaced temporally, that there is missing data, and because there are inconsistencies in the recording of events, there is inherent noise in the data. Additionally, the data can be boiled down to a list of the form {'Geyser Name' : 'Timestamp'}, thus while it intuitively seems to be time series data, there is no measured quantity corresponding to each time point.

**Data Processing**

To deal with these issues, I processed my data through a three step pipeline which can be called as the 'Transform-Filter-Smooth'.

1) In the transform step, I calculate a value with the variable name 't_nxt_eruption' that capture the time elapsed between two consequetive eruptions. Thus for each timestamp, I now have a corresponding measured value equal to the length of time untill the next eruption.

2) Because there were missing events between two consequentive recorded events, the value of 't_nxt_eruption' became very large for some time points. Plotting a histogram of t_nxt_eruption values revealed a long tailed distribution. In the 'Filter' step, I remove the long tail and thus pruning the data to a subset that is much cleaner.

3) Even after filtering the data, I observed that my data was still noisy. Hence, in the 'Smooth' step, I perform a smoothing procedure by averaging over a rolling window of 5 events.

**Fitting Time Series using Prophet and Validating Results**

This cleaned and processed data, I modeled using Prophet - a general purpose forecasting tool open sourced by Facebook.

All of the above steps are contained in the python notebook train_Prophet_Model.ipynb

I fit the model using data from Jan 2010 to May 2019 and tested the models on recorded eruptions from Jun-Sep 2019. 7 different models were fit for 7 geysers. I chose the Mean Absolute Error as my validation metric and for 6/7 geysers, the MAE is indeed low with the model uncertainty being lower than the NPS provided predictions. The Accuracy for 6/7 models ranges from 80-98% calculated using the time windows (or uncertainty) calculated by the models.

**Results available via a Dash Web-App hosted on AWS**

The models are 'pickled' and the python script run_Prophet_Predictions.py generates a csv files with the latest predictions starting from the most recent recorded eruption - it queries Geyser Times api to fetch the latest eruption data.

This csv is then rendered by the script GeyserWatch_webapp.py which is a Dash app displaying an interactive timeline of geyser eruptions. The webapp is hosted on AWS and is available at www.geyserwatch.xyz
