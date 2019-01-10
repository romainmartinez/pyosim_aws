import numpy as np

import opensim as osim
import pygmo as pg
from pyosim import MuscleAnalysis
from pyomeca import Analogs3d

from project_conf import MODELS_PATH, PROJECT_PATH, TEMPLATES_PATH

# Optimization strategy
#   optimize
#       the wrapping objects dimensions;
#   in order to
#       maximize R² with the template on muscle lengths and muscular moment arms;
#       minimize the difference with the first guesses;
#   such as
#       there is no discontinuity in muscle lengths;
#
# OBJECTIVE FUNCTION
#   Load the mot file (motion that recreates normal upper limb activity)
#   Perform the muscle analysis
#   Load the project_sample
#   Compute the R² of moment arms and muscle lengths between the scaled model and the non-scaled model
#   Minimize the R² and the difference with the first guess
#
# CONSTRAINT FUNCTION
#   Load the muscle analysis project_sample
#   Find any discontinuities (velocity of muscle lengths > mean_rms * 10)

#
# NOTE : For some reason, in debug opensim writes its sto file comma decimal instead of point decimal...
model = 'wu'
subject = 'mars'

template_model = f'{MODELS_PATH}/{model}.osim'
subject_model = f'{PROJECT_PATH}/{subject}/_models/{model}_scaled.osim'
# mot_file = f'{model}_optimMotion.mot'
mot_file = f'{model}_MarSF12H1_2.mot'

# Load osim files
runningOpenSimModels = {}
nb_population = 10


def get_open_sim_model(prob):
    if prob in runningOpenSimModels:
        return runningOpenSimModels[prob][0], runningOpenSimModels[prob][1], runningOpenSimModels[prob][2], runningOpenSimModels[prob][3], runningOpenSimModels[prob][4]
    else:
        runningOpenSimModels[prob] = [osim.Model(subject_model), get_open_sim_model.idx]
        runningOpenSimModels[prob].append(runningOpenSimModels[prob][0].initSystem())

        data_storage = osim.Storage(f'{PROJECT_PATH}/{subject}/1_inverse_kinematic/{mot_file}')

        model = runningOpenSimModels[prob][0]
        model.getSimbodyEngine().convertDegreesToRadians(data_storage)
        data_storage.lowpassFIR(2, 6)
        gen_coord_function = osim.GCVSplineSet(5, data_storage)
        runningOpenSimModels[prob].append(list())
        for frame in range(data_storage.getSize()):
            q = list()
            for idx_q in range(data_storage.getStateVector(frame).getSize()):
                q.append(gen_coord_function.evaluate(idx_q, 0, data_storage.getStateVector(frame).getTime()))
            runningOpenSimModels[prob][3].append(osim.Vector(q))
        runningOpenSimModels[prob].append(np.linspace(data_storage.getFirstTime(), data_storage.getLastTime(), num=data_storage.getSize()))

        get_open_sim_model.idx += 1
        return runningOpenSimModels[prob][0], runningOpenSimModels[prob][1], runningOpenSimModels[prob][2], runningOpenSimModels[prob][3], runningOpenSimModels[prob][4]
get_open_sim_model.idx = 0


def generate_motion(resolution=100):
    # At beginning, I was in the hope that I could recursively call the function in order to do an exhaustive scan
    # of the ranges of motion.
    # Unless better idea comes, it raises an out of memory because the matrix is [resolution^len(dofs)] long
    # The strategy now is to concatenate different gestures

    final_array = np.ndarray((resolution, len(dofs) + 1))
    final_array[:, 14] = np.linspace(0, np.pi / 2, resolution)
    final_array[:, 0] = np.linspace(0, (resolution - 1) / 100, resolution)
    return final_array


def generate_mot_file(path_to_save, data):
    if len(dofs) != data.shape[1] - 1:  # -1 for the time column
        raise ValueError("Wrong number of dofs")

    # Prepare the header
    header = list()
    header.append(f"Coordinates\nversion=1\nnRows={data.shape[0]}\n"
                  f"nColumns={data.shape[1]}\ninDegrees=no\nendheader\n")
    header.append("time\t")
    for dof in dofs:
        header.append(f"{dof}\t")
    header = ''.join(header)

    # Write the data
    np.savetxt(path_to_save, data, delimiter='\t', header=header, comments='')


# Generate a mot file which can create muscles discontinuity and get all degrees of freedom of the model
osim_generic = osim.Model(subject_model)
dofs = list()
for i in range(osim_generic.get_JointSet().getSize()):
    for j in range(osim_generic.get_JointSet().get(i).numCoordinates()):
        dofs.append(osim_generic.get_JointSet().get(i).get_coordinates(j).getName())
generate_mot_file(f'{PROJECT_PATH}/{subject}/temp_optim_wrap/{mot_file}', generate_motion())


class WrapOptim:
    def __init__(self):
        self.osim_model = -1
        self.output_path = ""
        self.muscle_length_path = ""

        # Do a first muscle analysis
        self.data_of_the_subject = Analogs3d(np.ndarray((0, 0)))
        self.data_template = Analogs3d(np.ndarray((0, 0)))
        self.analyse_must_be_perform = True
        self.initialSizes = []

    def get_osim_model(self):
        osim_model, idx, state, all_q, time_frames = get_open_sim_model(self)
        if self.osim_model != idx:
            self.osim_model = idx
            self.output_path = f'template_temp_optim_wrap_{self.osim_model}'
            self.muscle_length_path = f"{(PROJECT_PATH / subject / self.output_path / f'{mot_file[:-4]}_MuscleAnalysis_Length.sto').resolve()}"

            # Do a first muscle analysis
            self.data_of_the_subject = Analogs3d(np.ndarray((0, 0)))
            self.analyse_must_be_perform = True
            self.perform_muscle_analysis_derivative(template_model)
            self.data_template = self.data_of_the_subject
            self.analyse_must_be_perform = True
            self.perform_muscle_analysis_derivative(subject_model)

            # Remember initial sizes
            # Waitin opensim API to be ready
            self.initialSizes = np.array([0.1, 0.1, 0.1])  # for now suppose only one wrap
            # wraps = self.get_wrappings()
            # for i in range(len(wraps)):
            #     wrapEll = osim.WrapEllipsoid.safeDownCast(wraps[i])
            #     if wrapEll:
            #         pass
            #         # Waiting for opensim api to be ready
            #         # self.initialSizes.append(np.array(wrapEll.get_dimensions()))
            #
            #     wrapCyl = osim.WrapCylinder.safeDownCast(wraps[i])
            #     if wrapCyl:
            #         pass
            #         # Waiting for opensim api to be ready
            #         # self.initialSizes.append(np.array(wrapCyl.get_dimensions()))
            #
            #     wrapTor = osim.WrapTorus.safeDownCast(wraps[i])
            #     if wrapTor:
            #         pass
            #         # Waiting for opensim api to be ready
            #         # self.initialSizes.append(np.array(wrapTor.get_dimensions()))
            #
            #     wrapSphere = osim.WrapSphere.safeDownCast(wraps[i])
            #     if wrapSphere:
            #         pass
            #         # Waiting for opensim api to be ready
            #         # self.initialSizes.append(np.array(wrapSphere.get_dimensions()))

        return osim_model

    @staticmethod
    def get_name():
        return "Wu optim"

    @staticmethod
    def get_nobj():
        return 29 + 3  # 29 muscles + 3 wrappings

    @staticmethod
    def get_nic():
        return 29  # 29 muscles

    @staticmethod
    def get_bounds():
        return np.zeros(3).tolist(), (np.ones(3)).tolist()

    def get_wrappings(self):
        # Get all the references to wrapping objects and return them into a list
        wraps = list()
        bs = self.get_osim_model().get_BodySet()
        for i in range(bs.getSize()):
            w = bs.get(i).get_WrapObjectSet()
            for j in range(w.getSize()):
                wraps.append(w.get(j))

        return wraps

    def set_wrappings(self, x):
        # Get all the wrappings references
        wrappings = self.get_wrappings()

        # Fill them with x
        # Waiting for the API to be ready
        wraps = self.get_wrappings()
        for i in range(len(wraps)):
            wrapEll = osim.WrapEllipsoid.safeDownCast(wraps[i])
            if wrapEll:
                pass
                # Waiting for opensim api to be ready
                # wrapEll.set_dimensions(x[3*i:3*i+2])

            wrapCyl = osim.WrapCylinder.safeDownCast(wraps[i])
            if wrapCyl:
                pass
                # Waiting for opensim api to be ready
                # wrapCyl.set_dimensions(x[3*i:3*i+2])

            wrapTor = osim.WrapTorus.safeDownCast(wraps[i])
            if wrapTor:
                pass
                # Waiting for opensim api to be ready
                # wrapTor.set_dimensions(x[3*i:3*i+2])

            wrapSphere = osim.WrapSphere.safeDownCast(wraps[i])
            if wrapSphere:
                pass
                # Waiting for opensim api to be ready
                # wrapSphere.set_dimensions(x[3*i:3*i+2])

        # Remember that something was modified
        self.analyse_must_be_perform = True

    def perform_muscle_analysis_derivative(self, path_model):
        if self.analyse_must_be_perform:
            model, idx, state, all_q, time_frames = get_open_sim_model(self)

            lengths = list()
            for frame in all_q:
                state.setQ(frame)
                model.realizePosition(state)
                model.equilibrateMuscles(state)
                muscles = model.getMuscles()
                lengths.append([muscles.get(m).getLength(state) for m in range(muscles.getSize())])
                # muscles.get(0).computeMomentArm(state, corresponding_q)

            a = Analogs3d(np.array(lengths))
            a.get_time_frames = time_frames
            self.data_of_the_subject = a.derivative().abs()[:, :, 1:-1]

    def continuous_muscle_constraint(self):
        # Inequality constraint.
        # If muscle length top 2% change in velocity is lower than mean_rms * 10, we assume all muscles are continuous
        self.perform_muscle_analysis_derivative(subject_model)

        mean_rms = np.mean(self.data_of_the_subject.rms())
        return np.percentile(self.data_of_the_subject, 99.9, axis=2) - mean_rms * 10

    def fitness(self, x):
        self.set_wrappings(x)

        # Compute R² (first objective)
        self.perform_muscle_analysis_derivative(subject_model)
        corrcoef = list()
        for dof in range(self.data_of_the_subject.shape[1]):
            coef = np.corrcoef(self.data_of_the_subject[0, dof, :], self.data_template[0, dof, :])[1, 0]
            if np.isnan(coef):
                val = 0
            else:
                val = coef * coef  # (R^2)
            corrcoef.append(val)

        # Minimize change with original size
        size_fitness = np.square(self.initialSizes - x).tolist()
        print(self.initialSizes)
        print(x)

        # Inequality constraints
        ineq_const = self.continuous_muscle_constraint()[0, :].tolist()

        # Concat objective / equality / inequality
        return corrcoef + size_fitness + ineq_const


class WrapOptimSingleObjective(WrapOptim):
    def __init__(self):
        super().__init__()

    def get_nobj(self):
        return 1

    def fitness(self, x):
        old_fitness = super().fitness(x)
        final_fitness = 0
        for idx in range(super().get_nobj()):
            final_fitness += old_fitness[idx] * old_fitness[idx]
        return [final_fitness] + old_fitness[super().get_nobj():]


class WrapOptimSingleObjectiveUnconstraint(WrapOptim):
    def __init__(self):
        super().__init__()
        self.constraint_penalty = 1000

    def get_nobj(self):
        return 1

    def get_nic(self):
        return 0

    def fitness(self, x):
        old_fitness = super().fitness(x)
        final_fitness = 0
        for idx in range(super().get_nobj()):
            final_fitness += old_fitness[idx] * old_fitness[idx]
        for idx in range(super().get_nic()):
            if old_fitness[idx] > 0:
                final_fitness += old_fitness[idx] * old_fitness[idx] * self.constraint_penalty
        return [final_fitness]


prob = pg.problem(WrapOptimSingleObjectiveUnconstraint())
pop = pg.population(prob, size=nb_population)
algo = pg.algorithm(uda=pg.pso(gen=50))
pop = algo.evolve(pop)
print(pop)
