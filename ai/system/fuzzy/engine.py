import numpy as np
import pandas as pd

from system.fuzzy.componentes.nitrogen import NitrogenLevel
from system.fuzzy.componentes.physical import PhysicalConditions
from system.fuzzy.componentes.nutrients import NutrientLevel
from system.fuzzy.componentes.aditional import AdditionalConditions
from system.fuzzy.componentes.chemical import ChemicalConditions
from system.fuzzy.componentes.eutrophication import EutrophicationLevel
from system.fuzzy.componentes.oxygen import OxygenBalance
from system.fuzzy.componentes.solids import SolidsLevel
from system.fuzzy.componentes.visibility import VisibilityLevel
from system.fuzzy.componentes.phosphorus import PhosphorusLevel

class FuzzyEngine:
    def __init__(self, **kwargs) -> None:
        self.phase = 4
        self.vars = kwargs

        self.inputs = {}

        self.chain = {
            'nitrogen_level': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'phosphorus_level': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'oxygen_balance': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'solids_level': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'visibility_level': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'additional_conditions': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'physical_conditions': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'nutrient_level': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'chemical_conditions': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            },
            'eutrophication_level': {
                'vars': '-',
                'confidence': 0.0,
                'value': np.nan,
                'label': 'UNKNOWN'
            }
        }

        self.errors = {}

    def set_phase(self, *, phase: int) -> None:
        self.phase = phase

    def run(self) -> None:
        if self.phase >= 1:
            self._infer_nitrogen_level()
            self._infer_phosphorus_level()
            self._infer_oxygen_balance()
            self._infer_solids_level()
            self._infer_visibility_level()
            self._infer_additional_conditions()

            confidence_phase_1 = (
                self.chain['nitrogen_level']['confidence'] +
                self.chain['phosphorus_level']['confidence'] +
                self.chain['oxygen_balance']['confidence'] +
                self.chain['solids_level']['confidence'] +
                self.chain['visibility_level']['confidence'] +
                self.chain['additional_conditions']['confidence']
            ) / 6.0

        if self.phase >= 2:

            self._infer_nutrient_level()
            confidence_phase_2 = self.chain['nutrient_level']['confidence']

        if self.phase >= 3:
            self._inferir_physical_conditions()
            self._infer_chemical_conditions()
            confidence_phase_3 = (
                self.chain['physical_conditions']['confidence'] +
                self.chain['chemical_conditions']['confidence']
            ) / 2.0

        if self.phase >= 4:
            self._infer_eutrophication_level()

            confidence_phase_4 = self.chain['eutrophication_level']['confidence']
            confidence_final = (
                confidence_phase_1 +
                confidence_phase_2 +
                confidence_phase_3 +
                confidence_phase_4
            ) / 4.0

            self.chain['eutrophication_level']['confidence'] = confidence_final

    def _infer_nitrogen_level(self) -> None:
        try:
            model = NitrogenLevel(**self.vars)
            vars = model.calculate_inference()
            value = model.nitrogen_level
            label = model.get_label()

            self.inputs['nitrogen_level'] = model.available_vars

            self.chain['nitrogen_level']['vars'] = vars
            self.chain['nitrogen_level']['confidence'] = 1.0
            self.chain['nitrogen_level']['value'] = value
            self.chain['nitrogen_level']['label'] = label

        except Exception as e:
            self.errors['nitrogen_level'] = str(e)

    def _infer_phosphorus_level(self) -> None:
        try:
            model = PhosphorusLevel(**self.vars)
            vars = model.calculate_inference()
            value = model.phosphorus_level
            label = model.get_label()

            self.inputs['phosphorus_level'] = model.available_vars

            self.chain['phosphorus_level']['vars'] = vars
            self.chain['phosphorus_level']['confidence'] = 1.0
            self.chain['phosphorus_level']['value'] = value
            self.chain['phosphorus_level']['label'] = label

        except Exception as e:
            self.errors['phosphorus_level'] = str(e)

    def _infer_oxygen_balance(self) -> None:
        try:
            model = OxygenBalance(**self.vars)
            vars = model.calculate_inference()
            value = model.oxygen_balance
            label = model.get_label()

            self.inputs['oxygen_balance'] = model.available_vars

            self.chain['oxygen_balance']['vars'] = vars
            self.chain['oxygen_balance']['confidence'] = 1.0
            self.chain['oxygen_balance']['value'] = value
            self.chain['oxygen_balance']['label'] = label

        except Exception as e:
            self.errors['oxygen_balance'] = str(e)

    def _infer_solids_level(self) -> None:
        try:
            model = SolidsLevel(**self.vars)
            vars = model.calculate_inference()
            value = model.solids_level
            label = model.get_label()

            self.inputs['solids_level'] = model.available_vars

            self.chain['solids_level']['vars'] = vars
            self.chain['solids_level']['confidence'] = 1.0
            self.chain['solids_level']['value'] = value
            self.chain['solids_level']['label'] = label

        except Exception as e:
            self.errors['solids_level'] = str(e)

    def _infer_visibility_level(self) -> None:
        try:
            model = VisibilityLevel(**self.vars)
            vars = model.calculate_inference()
            value = model.visibility_level
            label = model.get_label()

            self.inputs['visibility_level'] = model.available_vars

            self.chain['visibility_level']['vars'] = vars
            self.chain['visibility_level']['confidence'] = 1.0
            self.chain['visibility_level']['value'] = value
            self.chain['visibility_level']['label'] = label

        except Exception as e:
            self.errors['visibility_level'] = str(e)

    def _infer_additional_conditions(self) -> None:
        try:
            model = AdditionalConditions(**self.vars)

            vars, confidence = model.calculate_inference()
            value = model.additional_conditions
            label = model.get_label()

            self.inputs['additional_conditions'] = model.available_vars

            self.chain['additional_conditions']['vars'] = vars
            self.chain['additional_conditions']['confidence'] = confidence
            self.chain['additional_conditions']['value'] = value
            self.chain['additional_conditions']['label'] = label

        except Exception as e:
            self.errors['additional_conditions'] = str(e)

    def _inferir_physical_conditions(self) -> None:
        try:
            model = PhysicalConditions(
                solids_level=self.chain['solids_level']['value'],
                visibility_level=self.chain['visibility_level']['value']
            )

            vars, confidence = model.calculate_inference()
            value = model.physical_conditions
            label = model.get_label()

            self.chain['physical_conditions']['vars'] = vars
            self.chain['physical_conditions']['confidence'] = confidence
            self.chain['physical_conditions']['value'] = value
            self.chain['physical_conditions']['label'] = label

        except Exception as e:
            self.errors['physical_conditions'] = str(e)

    def _infer_nutrient_level(self) -> None:
        try:
            model = NutrientLevel(
                nitrogen_level=self.chain['nitrogen_level']['value'],
                phosphorus_level=self.chain['phosphorus_level']['value'],
            )

            vars, confidence = model.calculate_inference()
            value = model.nutrient_level
            label = model.get_label()

            self.chain['nutrient_level']['vars'] = vars
            self.chain['nutrient_level']['confidence'] = confidence
            self.chain['nutrient_level']['value'] = value
            self.chain['nutrient_level']['label'] = label

        except Exception as e:
            self.errors['nutrient_level'] = str(e)

    def _infer_chemical_conditions(self) -> None:
        try:
            model = ChemicalConditions(
                nutrient_level=self.chain['nutrient_level']['value'],
                oxygen_balance=self.chain['oxygen_balance']['value'],
            )

            vars, confidence = model.calculate_inference()
            value = model.chemical_conditions
            label = model.get_label()

            self.chain['chemical_conditions']['vars'] = vars
            self.chain['chemical_conditions']['confidence'] = confidence
            self.chain['chemical_conditions']['value'] = value
            self.chain['chemical_conditions']['label'] = label

        except Exception as e:
            self.errors['chemical_conditions'] = str(e)

    def _infer_eutrophication_level(self) -> None:
        try:
            model = EutrophicationLevel(
                chemical_conditions=self.chain['chemical_conditions']['value'],
                physical_conditions=self.chain['physical_conditions']['value'],
                additional_conditions=self.chain['additional_conditions']['value']
            )

            vars, confidence = model.calculate_inference()
            value = model.eutrophication_level
            label = model.get_label()

            self.chain['eutrophication_level']['vars'] = vars
            self.chain['eutrophication_level']['confidence'] = confidence
            self.chain['eutrophication_level']['value'] = value
            self.chain['eutrophication_level']['label'] = label

        except Exception as e:
            self.errors['eutrophication_level'] = str(e)


def execute_engine(df: pd.DataFrame) -> tuple[list, list, list]:
    results = []
    inputs = []
    errors = []

    for _, row in df.iterrows():
        motor = FuzzyEngine(**row.to_dict())
        motor.run()

        results.append(motor.chain)
        inputs.append(motor.inputs)
        errors.append(motor.errors)

    return results, inputs, errors