from experiments.scp_experiment import SCP_Experiment
from utils import utils
def main():
    # 这两个路径只是在构造 SCP_Experiment 时占位用，
    # evaluate() 实际只依赖 outputfolder 和 experiment_name
    datafolder_ptbxl = '../data/ptbxl/'
    datafolder_icbeb = '../data/ICBEB/'
    outputfolder = '../output/'

    # 只用来构造对象，evaluate() 不会用到 self.models
    models = []

    ##########################################
    # 1. 只基于已有预测，补算 PTB-XL 各实验的结果表
    ##########################################
    experiments = [
        ('exp0', 'all'),
        ('exp1', 'diagnostic'),
        ('exp1.1', 'subdiagnostic'),
        ('exp1.1.1', 'superdiagnostic'),
        ('exp2', 'form'),
        ('exp3', 'rhythm'),
    ]

    for name, task in experiments:
        e = SCP_Experiment(name, task, datafolder_ptbxl, outputfolder, models)
        # 只做一次整体评估，不做 bootstrap，加快速度且避免多进程问题
        e.evaluate(bootstrap_eval=False, n_jobs=1)

    # 生成 PTB-XL 汇总表
    utils.generate_ptbxl_summary_table()

    ##########################################
    # 2. 只基于已有预测，补算 ICBEB 实验的结果表
    ##########################################
    e = SCP_Experiment('exp_ICBEB', 'all', datafolder_icbeb, outputfolder, models)
    e.evaluate(bootstrap_eval=False, n_jobs=1)

    # 生成 ICBEB 汇总表
    utils.ICBEBE_table()


if __name__ == "__main__":
    main()

