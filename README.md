# GeyserWatch
Predicting geyser eruptions at Yellowstone National Park

www.geyserwatch.xyz

4 Million visitors come to the Yellowstone National Park annually to experience the unique geo-thermal activity of the area, and witness the spectacular geyser eruptions. They rely on the predictions provided by the National Park Service to plan their day, however the predictions often range from	±45 minutes to ±2 hours making it impractical to plan around the uncertainty.

I sought to improve upon these prediction windows and for that I first acccessed historical data from the archives of Geyser Times : https://geysertimes.org/archive/ . Geyser Times provides free access to historical geyser eruption data and updated nightly.

After a bit of data cleaning, preliminary EDA revealed various aspects of the data. The python notebook data_Cleanup_EDA.ipynb contains the relevant steps as well as the EDA plots. From the plots its clear that the data is irregularly spaced temporally, that there is missing data, and because there are inconsistencies in the recording of events, there is inherent noise in the data. Additionally, the data can be boiled down to a list of the form {'Geyser Name' : 'Timestamp'}, thus while it intuitively seems to be timeseries data, there is no measured quantity corresponding to each time point.

To deal with these issues, I process my data through a pipeline which I call as the 'Transform-Filter-Smooth'. In the transform step, I calculate a value with the variable name 't_nxt_eruption' that capture the time elapsed between two consequetive eruptions. Thus for each timestamp, I now have a corresponding measured value equal to the length of time untill the next eruption. In case there are missing events between two consequentive recorded events, the value of 't_nxt_eruption' becomes very large and hence plotting the histogram of the values reveals a long tailed distribution. I filter the distribution to remove the long tail and thus filter missing data.

Even after removing a lot of the missing data, my raw data is noisy, and hence I do a smoothing procedure by averaging over a rolling window of 5 events.

This data, I model using Prophet - a general purpose forecasting tool open sourced by Facebook.

The above steps can be seen in the python notebook train_Prophet_Model.ipynb

The models are 'pickled' and the python script run_Prophet_Predictions.py can generate a csv files with the latest predictions starting from the most recent recorded eruption - it queries Geyser Times api to fetch the latest eruption data.

This csv is then rendered by the script GeyserWatch_webapp.py which is a Dash app displaying an interactive timeline of geyser eruptions. The webapp is hosted on AWS and is available at www.geyserwatch.xyz
