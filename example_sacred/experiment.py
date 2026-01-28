
import numpy as np
import matplotlib.pyplot as plt


## Sacred specific imports 

# Experiment: Central class of Sacred framework, specifyes config, main function, observers, etc.
from sacred import Experiment

# Ingredient: Tasks that can be reused across experiments
from ingredient_save_folder import save_folder, make_folder

# Observer: Used to log experiment results to different backends
from sacred.observers import MongoObserver


ex = Experiment('test_experiment', ingredients=[save_folder])

ex.observers.append(MongoObserver(url='mongodb://localhost:27017/',
                                  db_name='test_db'))



@ex.config
def my_config():
    A = 10
    tau = 0.5
    B = 3
    N = 100
    t_max = 1.0


@ex.capture
def get_exponential(A, tau, B, N, t_max):
    x = np.linspace(0, t_max, N)
    y = A * np.exp(-tau * x) + B
    return x, y

@ex.automain
def my_main(_run, _log):

    save_folder =  make_folder(_run, root = "")

    x, y = get_exponential()

    plt.plot(x, y)
    plt.xlabel('time')
    plt.ylabel('y')
    plt.savefig(save_folder + '/output_plot.png')
    _log.info("Saved output plot to {}".format(save_folder + '/output_plot.png'))

    ex.add_artifact(save_folder + '/output_plot.png', name='output_plot.png')

    for i in range(len(y)):
        _run.log_scalar("y", y[i], x[i])


    