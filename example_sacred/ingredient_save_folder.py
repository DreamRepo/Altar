"""
  
  Copyright (C) 2022 Sony Computer Science Laboratories
  
  Author(s) Aliénor Lahlou
  
  free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful, but
  WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
  General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program.  If not, see
  <http://www.gnu.org/licenses/>.
  
"""

import numpy as np
from sacred import Ingredient
import json
import os
import datetime

import os



save_folder = Ingredient('save_folder')

#ref: https://www.programmerall.com/article/57461489186/
class np_encode(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(MyEncoder, self).default(obj)
        


@save_folder.config
def cfg():
    folder = ""


@save_folder.capture
def make_folder(_run, root = "./"):
    experiments_root = os.path.join(root, "Experiments")

    # Safely create the base Experiments directory if it does not exist yet
    os.makedirs(experiments_root, exist_ok=True)


    folder = os.path.join(
        experiments_root,
        str(_run._id) + "_" + str(datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_')) + _run.experiment_info["name"],
    )

    os.mkdir(folder)
    with open(folder + '/config.json', 'w') as fp:
        json.dump(_run.config, fp, cls=np_encode)

    return folder


