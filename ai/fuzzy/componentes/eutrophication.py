import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class NivelEutrofizacion:
    def __init__(
        self,
        condiciones_quimicas=np.nan,
        condiciones_fisicas=np.nan,
        condiciones_adicionales=np.nan,
    ):
        self.condiciones_quimicas = condiciones_quimicas
        self.condiciones_fisicas = condiciones_fisicas
        self.condiciones_adicionales = condiciones_adicionales
        self.nivel_eutrofizacion = np.nan

        # Verificar que al menos una variable esté disponible
        if np.isnan(self.condiciones_quimicas) and np.isnan(self.condiciones_fisicas) and np.isnan(self.condiciones_adicionales):
            raise ValueError("Se requiere al menos condiciones_quimicas, condiciones_fisicas o condiciones_adicionales para evaluar el nivel de eutrofización.")

        # Determinar variables disponibles
        self.variables_disponibles = []
        if not np.isnan(self.condiciones_quimicas):
            self.variables_disponibles.append('condiciones_quimicas')
        if not np.isnan(self.condiciones_fisicas):
            self.variables_disponibles.append('condiciones_fisicas')
        if not np.isnan(self.condiciones_adicionales):
            self.variables_disponibles.append('condiciones_adicionales')

        # Crear el sistema difuso según las variables disponibles
        self._crear_sistema_difuso()

    def _crear_sistema_difuso(self):
        # Definir la variable de salida
        self.nivel_eutrofizacion_universe = np.arange(0, 1.01, 0.01)
        self.nivel_eutrofizacion_var = ctrl.Consequent(self.nivel_eutrofizacion_universe, 'nivel_eutrofizacion')
        self.nivel_eutrofizacion_var['OLIGOTRÓFICO'] = fuzz.trapmf(self.nivel_eutrofizacion_var.universe, [0, 0, 0.2, 0.3])
        self.nivel_eutrofizacion_var['MESOTRÓFICO'] = fuzz.trimf(self.nivel_eutrofizacion_var.universe, [0.25, 0.4, 0.55])
        self.nivel_eutrofizacion_var['EUTRÓFICO'] = fuzz.trimf(self.nivel_eutrofizacion_var.universe, [0.5, 0.65, 0.8])
        self.nivel_eutrofizacion_var['HIPEREUTRÓFICO'] = fuzz.trapmf(self.nivel_eutrofizacion_var.universe, [0.75, 0.85, 1, 1])

        self.rules = []
        self.variables = {}

        # Definir variables difusas según las variables disponibles
        if 'condiciones_quimicas' in self.variables_disponibles:
            # Definir el universo de discurso para condiciones_quimicas
            self.condiciones_quimicas_universe = np.arange(0, 1.01, 0.01)
            self.condiciones_quimicas_var = ctrl.Antecedent(self.condiciones_quimicas_universe, 'condiciones_quimicas')
            self.condiciones_quimicas_var['BUENAS'] = fuzz.trapmf(self.condiciones_quimicas_var.universe, [0, 0, 0.2, 0.35])
            self.condiciones_quimicas_var['NEUTRALES'] = fuzz.trimf(self.condiciones_quimicas_var.universe, [0.3, 0.45, 0.6])
            self.condiciones_quimicas_var['MALAS'] = fuzz.trimf(self.condiciones_quimicas_var.universe, [0.55, 0.7, 0.85])
            self.condiciones_quimicas_var['MUY MALAS'] = fuzz.trapmf(self.condiciones_quimicas_var.universe, [0.8, 0.9, 1, 1])
            self.variables['condiciones_quimicas'] = self.condiciones_quimicas_var

        if 'condiciones_fisicas' in self.variables_disponibles:
            # Definir el universo de discurso para condiciones_fisicas
            self.condiciones_fisicas_universe = np.arange(0, 1.01, 0.01)
            self.condiciones_fisicas_var = ctrl.Antecedent(self.condiciones_fisicas_universe, 'condiciones_fisicas')
            self.condiciones_fisicas_var['BUENAS'] = fuzz.trapmf(self.condiciones_fisicas_var.universe, [0, 0, 0.2, 0.3])
            self.condiciones_fisicas_var['NEUTRALES'] = fuzz.trimf(self.condiciones_fisicas_var.universe, [0.25, 0.4, 0.55])
            self.condiciones_fisicas_var['MALAS'] = fuzz.trimf(self.condiciones_fisicas_var.universe, [0.5, 0.65, 0.8])
            self.condiciones_fisicas_var['MUY MALAS'] = fuzz.trapmf(self.condiciones_fisicas_var.universe, [0.75, 0.85, 1, 1])
            self.variables['condiciones_fisicas'] = self.condiciones_fisicas_var

        if 'condiciones_adicionales' in self.variables_disponibles:
            self.condiciones_adicionales_universe = np.arange(0, 1.01, 0.01)
            self.condiciones_adicionales_var = ctrl.Antecedent(self.condiciones_adicionales_universe, 'condiciones_adicionales')
            self.condiciones_adicionales_var['DESFAVORABLES'] = fuzz.trapmf(self.condiciones_adicionales_var.universe, [0, 0, 0.2, 0.4])
            self.condiciones_adicionales_var['NEUTRALES'] = fuzz.trimf(self.condiciones_adicionales_var.universe, [0.3, 0.5, 0.7])
            self.condiciones_adicionales_var['FAVORABLES'] = fuzz.trapmf(self.condiciones_adicionales_var.universe, [0.6, 0.8, 1, 1])
            self.variables['condiciones_adicionales'] = self.condiciones_adicionales_var


        # Definir las reglas difusas según las variables disponibles
        self._definir_reglas()

        # Crear el sistema de control
        self.control_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.control_system)

    def _definir_reglas(self):
        # Reglas basadas en las variables disponibles
        if 'condiciones_quimicas' in self.variables and 'condiciones_fisicas' in self.variables and 'condiciones_adicionales' in self.variables:
            # Todas las variables están disponibles
            quimicas = self.variables['condiciones_quimicas']
            fisicas = self.variables['condiciones_fisicas']
            adicionales = self.variables['condiciones_adicionales']

            # Regla 1a
            self.rules.append(ctrl.Rule(
                quimicas['BUENAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES'] | fisicas['MALAS']) & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['OLIGOTRÓFICO']
            ))

            # Regla 1b
            self.rules.append(ctrl.Rule(
                quimicas['BUENAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES'] | fisicas['MALAS']) & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['OLIGOTRÓFICO']
            ))

            # Regla 1c
            self.rules.append(ctrl.Rule(
                quimicas['BUENAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES'] | fisicas['MALAS']) & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 2a
            self.rules.append(ctrl.Rule(
                quimicas['BUENAS'] & fisicas['MUY MALAS'] & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['OLIGOTRÓFICO']
            ))

            # Regla 2b
            self.rules.append(ctrl.Rule(
                quimicas['BUENAS'] & fisicas['MUY MALAS'] & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 2c
            self.rules.append(ctrl.Rule(
                quimicas['BUENAS'] & fisicas['MUY MALAS'] & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 3a
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & fisicas['BUENAS'] & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['OLIGOTRÓFICO']
            ))

            # Regla 3b
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & fisicas['BUENAS'] & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['OLIGOTRÓFICO']
            ))

            # Regla 3c
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & fisicas['BUENAS'] & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 4a
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & fisicas['NEUTRALES'] & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['OLIGOTRÓFICO']
            ))

            # Regla 4b
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & fisicas['NEUTRALES'] & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 4c
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & fisicas['NEUTRALES'] & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 5a
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & (fisicas['MALAS'] | fisicas['MUY MALAS']) & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 5b
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & (fisicas['MALAS'] | fisicas['MUY MALAS']) & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 5c
            self.rules.append(ctrl.Rule(
                quimicas['NEUTRALES'] & (fisicas['MALAS'] | fisicas['MUY MALAS']) & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']
            ))

            # Regla 6a
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & fisicas['BUENAS'] & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['OLIGOTRÓFICO']
            ))

            # Regla 6b
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & fisicas['BUENAS'] & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 6c
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & fisicas['BUENAS'] & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 7a
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & (fisicas['NEUTRALES'] | fisicas['MALAS']) & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 7b
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & (fisicas['NEUTRALES'] | fisicas['MALAS']) & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 7c
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & (fisicas['NEUTRALES'] | fisicas['MALAS']) & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']
            ))

            # Regla 8a
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & fisicas['MUY MALAS'] & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 8b
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & fisicas['MUY MALAS'] & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']
            ))

            # Regla 8c
            self.rules.append(ctrl.Rule(
                quimicas['MALAS'] & fisicas['MUY MALAS'] & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']
            ))

            # Regla 9a
            self.rules.append(ctrl.Rule(
                quimicas['MUY MALAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES']) & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['MESOTRÓFICO']
            ))

            # Regla 9b
            self.rules.append(ctrl.Rule(
                quimicas['MUY MALAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES']) & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 9c
            self.rules.append(ctrl.Rule(
                quimicas['MUY MALAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES']) & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']
            ))

            # Regla 10a
            self.rules.append(ctrl.Rule(
                quimicas['MUY MALAS'] & (fisicas['MALAS'] | fisicas['MUY MALAS']) & adicionales['DESFAVORABLES'],
                self.nivel_eutrofizacion_var['EUTRÓFICO']
            ))

            # Regla 10b
            self.rules.append(ctrl.Rule(
                quimicas['MUY MALAS'] & (fisicas['MALAS'] | fisicas['MUY MALAS']) & adicionales['NEUTRALES'],
                self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']
            ))

            # Regla 10c
            self.rules.append(ctrl.Rule(
                quimicas['MUY MALAS'] & (fisicas['MALAS'] | fisicas['MUY MALAS']) & adicionales['FAVORABLES'],
                self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']
            ))

        elif 'condiciones_quimicas' in self.variables and 'condiciones_fisicas' in self.variables:
            # Ambas variables están disponibles
            quimicas = self.variables['condiciones_quimicas']
            fisicas = self.variables['condiciones_fisicas']

            self.rules.append(ctrl.Rule(quimicas['BUENAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES'] | fisicas['MALAS']), self.nivel_eutrofizacion_var['OLIGOTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['BUENAS'] & fisicas['MUY MALAS'], self.nivel_eutrofizacion_var['MESOTRÓFICO']))

            self.rules.append(ctrl.Rule(quimicas['NEUTRALES'] & fisicas['BUENAS'], self.nivel_eutrofizacion_var['OLIGOTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['NEUTRALES'] & (fisicas['NEUTRALES']), self.nivel_eutrofizacion_var['MESOTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['NEUTRALES'] & (fisicas['MALAS'] | fisicas['MUY MALAS']), self.nivel_eutrofizacion_var['EUTRÓFICO']))

            self.rules.append(ctrl.Rule(quimicas['MALAS'] & fisicas['BUENAS'], self.nivel_eutrofizacion_var['MESOTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['MALAS'] & (fisicas['NEUTRALES'] | fisicas['MALAS']), self.nivel_eutrofizacion_var['EUTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['MALAS'] & fisicas['MUY MALAS'], self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']))

            self.rules.append(ctrl.Rule(quimicas['MUY MALAS'] & (fisicas['BUENAS'] | fisicas['NEUTRALES']), self.nivel_eutrofizacion_var['EUTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['MUY MALAS'] & (fisicas['MALAS'] | fisicas['MUY MALAS']), self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']))
        
        elif 'condiciones_quimicas' in self.variables:
            # Solo condiciones químicas están disponibles
            quimicas = self.variables['condiciones_quimicas']
            self.rules.append(ctrl.Rule(quimicas['BUENAS'], self.nivel_eutrofizacion_var['OLIGOTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['NEUTRALES'], self.nivel_eutrofizacion_var['MESOTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['MALAS'], self.nivel_eutrofizacion_var['EUTRÓFICO']))
            self.rules.append(ctrl.Rule(quimicas['MUY MALAS'], self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']))

        elif 'condiciones_fisicas' in self.variables:
            # Solo condiciones fisicas están disponibles
            fisicas = self.variables['condiciones_fisicas']
            self.rules.append(ctrl.Rule(fisicas['BUENAS'], self.nivel_eutrofizacion_var['OLIGOTRÓFICO']))
            self.rules.append(ctrl.Rule(fisicas['NEUTRALES'], self.nivel_eutrofizacion_var['MESOTRÓFICO']))
            self.rules.append(ctrl.Rule(fisicas['MALAS'], self.nivel_eutrofizacion_var['EUTRÓFICO']))
            self.rules.append(ctrl.Rule(fisicas['MUY MALAS'], self.nivel_eutrofizacion_var['HIPEREUTRÓFICO']))

        elif 'condiciones_adicionales' in self.variables:
            adicionales = self.variables['condiciones_adicionales']
            self.rules.append(ctrl.Rule(adicionales['DESFAVORABLES'], self.nivel_eutrofizacion_var['OLIGOTRÓFICO']))
            self.rules.append(ctrl.Rule(adicionales['NEUTRALES'], self.nivel_eutrofizacion_var['MESOTRÓFICO']))
            self.rules.append(ctrl.Rule(adicionales['FAVORABLES'], self.nivel_eutrofizacion_var['EUTRÓFICO']))


    def calcular_inferencia(self):
        # Asignar los valores de entrada disponibles
        if 'condiciones_quimicas' in self.variables:
            self.simulation.input['condiciones_quimicas'] = self.condiciones_quimicas
        if 'condiciones_fisicas' in self.variables:
            self.simulation.input['condiciones_fisicas'] = self.condiciones_fisicas
        if 'condiciones_adicionales' in self.variables:
            self.simulation.input['condiciones_adicionales'] = self.condiciones_adicionales

        try:
            # Realizar la inferencia
            self.simulation.compute()

            # Obtener el resultado
            self.nivel_eutrofizacion = self.simulation.output['nivel_eutrofizacion']
        except Exception as e:
            raise ValueError(f"Error al calcular la inferencia: {e}")

        # Determinar variables usadas y confianza
        if 'condiciones_quimicas' in self.variables and 'condiciones_fisicas' in self.variables and 'condiciones_adicionales' in self.variables:
            variables_usadas = 'QUIMICAS_FISICAS_ADICIONALES'
            confianza = 1.0
        if 'condiciones_quimicas' in self.variables and 'condiciones_fisicas' in self.variables:
            variables_usadas = 'QUIMICAS_FISICAS'
            confianza = 0.9
        elif 'condiciones_quimicas' in self.variables:
            variables_usadas = 'QUIMICAS'
            confianza = 0.75
        elif 'condiciones_fisicas' in self.variables:
            variables_usadas = 'FISICAS'
            confianza = 0.4
        elif 'condiciones_adicionales' in self.variables:
            variables_usadas = 'ADICIONALES'
            confianza = 0.1

        return (variables_usadas, confianza)

    def obtener_etiqueta(self):
        if np.isnan(self.nivel_eutrofizacion):
            raise ValueError("No se ha calculado la inferencia del nivel de eutrofización.")

        # Determinar la etiqueta con mayor grado de pertenencia
        grados_pertenencia = {}
        for etiqueta in self.nivel_eutrofizacion_var.terms:
            funcion_pertenencia = self.nivel_eutrofizacion_var[etiqueta].mf
            grado = fuzz.interp_membership(self.nivel_eutrofizacion_var.universe, funcion_pertenencia, self.nivel_eutrofizacion)
            grados_pertenencia[etiqueta] = grado

        etiqueta_predicha = max(grados_pertenencia, key=grados_pertenencia.get)
        return etiqueta_predicha
