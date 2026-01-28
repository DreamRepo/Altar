from experiment import ex   



for tau in [0.1, 0.5, 1.0, 5, 10.0]:
    config_updates = {
        "A": 10,
        "tau": tau,
        "B": 0,
        "N": 100,
        "t_max": 1
    }
    
    
    print(f"Running Sacred experiment for {config_updates}")
    ex.run(config_updates=config_updates)




for i, N in enumerate([5, 10, 100, 1000]):
    config_updates = {
        "A": 10-i,
        "tau": tau,
        "B": 10+i,
        "N": N,
        "t_max": 1
    }
    
    
    print(f"Running Sacred experiment for {config_updates}")
    ex.run(config_updates=config_updates)


for i, t_max in enumerate([0.5, 1, 3]):
    config_updates = {
        "A": 10-i,
        "tau": tau,
        "B": 20+i,
        "N": 100,
        "t_max": t_max
    }
    
    
    print(f"Running Sacred experiment for {config_updates}")
    ex.run(config_updates=config_updates)