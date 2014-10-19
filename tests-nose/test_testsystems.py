import numpy as np

from simtk import unit
from simtk import openmm

import tempfile
import logging

import testsystems

def test_doctest():
    import doctest
    doctest.testmod(testsystems)

def test_properties_all_testsystems():
    testsystem_classes = testsystems.TestSystem.__subclasses__()
    logging.info("Testing analytical property computation:")
    for testsystem_class in testsystem_classes:
        class_name = testsystem_class.__name__
        logging.info(class_name)
        print class_name # DEBUG
        testsystem = testsystem_class()
        property_list = testsystem.analytical_properties
        state = testsystems.ThermodynamicState(temperature=300.0*unit.kelvin, pressure=1.0*unit.atmosphere)
        if len(property_list) > 0:
            for property_name in property_list:
                method = getattr(testsystem, 'get_' + property_name)
                logging.info("%32s . %32s : %32s" % (class_name, property_name, str(method(state))))

fast_testsystems = ["HarmonicOscillator", "PowerOscillator", "Diatom", "ConstraintCoupledHarmonicOscillator", "HarmonicOscillatorArray", "SodiumChlorideCrystal", "LennardJonesCluster", "LennardJonesFluid", "IdealGas", "AlanineDipeptideVacuum"]

def test_energy_all_testsystems():

    testsystem_classes = testsystems.TestSystem.__subclasses__()

    for testsystem_class in testsystem_classes:
        class_name = testsystem_class.__name__
        if class_name in fast_testsystems:
            logging.info("Testing potential energy test for testsystem %s" % class_name)
        else:
            logging.info("Skipping potential energy test for testsystem %s." % class_name)
            continue

        # Create system.
        testsystem = testsystem_class()

        # Create a Context.
        timestep = 1.0 * unit.femtoseconds
        integrator = openmm.VerletIntegrator(timestep)
        context = openmm.Context(testsystem.system, integrator)
        context.setPositions(testsystem.positions)

        # Compute potential energy to make sure it is finite.
        openmm_state = context.getState(getEnergy=True)
        potential_energy = openmm_state.getPotentialEnergy()

        # Check if finite.
        if np.isnan(potential_energy / unit.kilocalories_per_mole):
            raise Exception("Energy of test system %s is NaN." % class_name)

        # Clean up
        del context, integrator