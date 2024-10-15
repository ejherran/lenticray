# app/initial_data.py

from sqlalchemy.orm import Session
from app import models

def init_variables(db: Session) -> None:
    variables_data = [
        {"id": "DIN", "name": "Inorganic Nitrogen", "description": "Sum of Nitrite (NO2N), Nitrate (NO3N) and Total Ammonia Nitrogen (NH4N) in filtered samples.", "unit": "mg/l"},
        {"id": "DKN", "name": "Kjeldahl Nitrogen", "description": "Organic nitrogen and total ammonia nitrogen fractions in filtered samples, reported as nitrogen.", "unit": "mg/l"},
        {"id": "NH3N", "name": "Ammonia", "description": "Un-ionized ammonia (NH3), reported as Nitrogen.", "unit": "mg/l"},
        {"id": "NH4N", "name": "Ammonia", "description": "Combined un-ionized and ionized Ammonia (NH3 + NH4+), reported as Nitrogen", "unit": "mg/l"},
        {"id": "NOxN", "name": "Oxidized Nitrogen", "description": "Nitrate nitrogen and nitrite nitrogen fractions in unfiltered samples, reported as nitrogen.", "unit": "mg/l"},
        {"id": "NO2N", "name": "Oxidized Nitrogen", "description": "Reported as nitrogen.", "unit": "mg/l"},
        {"id": "NO3N", "name": "Oxidized Nitrogen", "description": "Reported as nitrogen.", "unit": "mg/l"},
        {"id": "PN", "name": "Total Nitrogen", "description": "Organic and inorganic nitrogen fractions retained by a filter, reported as nitrogen.", "unit": "mg/l"},
        {"id": "PON", "name": "Organic Nitrogen", "description": "Organic nitrogen fraction retained by a filter, reported as nitrogen.", "unit": "mg/l"},
        {"id": "TDN", "name": "Total Nitrogen", "description": "Organic and inorganic nitrogen fractions in filtered samples, reported as nitrogen.", "unit": "mg/l"},
        {"id": "TKN", "name": "Kjeldahl Nitrogen", "description": "Organic nitrogen and total ammonia nitrogen fractions in unfiltered samples, reported as nitrogen.", "unit": "mg/l"},
        {"id": "TN", "name": "Total Nitrogen", "description": "Organic and inorganic nitrogen fractions in unfiltered samples, reported as nitrogen.", "unit": "mg/l"},
        {"id": "TON", "name": "Organic Nitrogen", "description": "Organic nitrogen fractions in unfiltered samples, reported as nitrogen.", "unit": "mg/l"},
        {"id": "DON", "name": "Organic Nitrogen", "description": "Organic nitrogen fraction in filtered samples, reported as nitrogen.", "unit": "mg/l"},
        {"id": "DIP", "name": "Phosphate", "description": "Phosphate fractions in filtered samples responding to colorimetric tests after acid-hydrolysis (including dissolved reactive and acid-hydrolyzable phosphates), reported as phosphorus.", "unit": "mg/l"},
        {"id": "DRP", "name": "Orthophosphate", "description": "Phosphate fractions in filtered samples responding to colorimetric tests without preliminary acid-hydrolysis or oxidative digestion (largely a measure of orthophosphates), reported as phosphorus.", "unit": "mg/l"},
        {"id": "TDP", "name": "Phosphorus", "description": "Phosphate fractions in filtered samples responding to colorimetric tests after oxidative digestion (including dissolved reactive, acid-hydrolyzable and organic phosphates), reported as phosphorus.", "unit": "mg/l"},
        {"id": "TIP", "name": "Phosphate", "description": "Phosphate fractions in unfiltered samples responding to colorimetric tests after acid-hydrolysis (including total reactive and acid-hydrolyzable phosphates), reported as phosphorus.", "unit": "mg/l"},
        {"id": "TP", "name": "Phosphorus", "description": "Phosphate fractions in unfiltered samples responding to colorimetric tests after oxidative digestion of the unfiltered sample (including total reactive, acid-hydrolyzable and organic phosphates), reported as phosphorus.", "unit": "mg/l"},
        {"id": "TRP", "name": "Orthophosphate", "description": "Phosphate fractions in unfiltered samples responding to colorimetric tests without preliminary acid-hydrolysis or oxidative digestion (largely a measure of orthophosphates), reported as phosphorus.", "unit": "mg/l"},
        {"id": "TPP", "name": "Phosphorus", "description": "Phosphate fractions retained by a filter responding to colorimetric tests after oxidative digestion (including dissolved reactive, acid-hydrolyzable and organic phosphates), reported as phosphorus.", "unit": "mg/l"},
        {"id": "BOD", "name": "Oxygen Demand", "description": "A measure of oxygen consumption during decomposition of both organic and inorganic substances.", "unit": "mg/l"},
        {"id": "COD", "name": "Oxygen Demand", "description": "A measure of oxygen consumption during decomposition of organic and inorganic substances by a chemical oxidant.", "unit": "mg/l"},
        {"id": "O2_Dis", "name": "Oxygen", "description": "Concentration of molecular oxygen dissolved in water.", "unit": "mg/l"},
        {"id": "PV", "name": "Oxygen Demand", "description": "A measure for the concentration of material in a sample that is readily-oxidisable by potassium permanganate under acidic conditions. Reported as mg O2/L.", "unit": "mg/l"},
        {"id": "TDS", "name": "Dissolved Solids", "description": "Portion of solids that passes through a filter.", "unit": "mg/l"},
        {"id": "TS", "name": "Total Solids", "description": "Material residue left after evaporation of a sample and its subsequent drying at defined temperature.", "unit": "mg/l"},
        {"id": "TSS", "name": "Suspended Solids", "description": "Portion of solids retained by a filter.", "unit": "mg/l"},
        {"id": "FDS", "name": "Dissolved Solids", "description": "Residue of solids that pass through a filter and remain after heating to dryness for a specified time at a specified temperature.", "unit": "mg/l"},
        {"id": "FS", "name": "Total Solids", "description": "Residue of solids in an unfiltered sample that remain after heating to dryness for a specified time at a certain temperature.", "unit": "mg/l"},
        {"id": "VDS", "name": "Dissolved Solids", "description": "Weight loss of total dissolved solid fraction on ignition.", "unit": "mg/l"},
        {"id": "VS", "name": "Total Solids", "description": "Weight loss of total solids on ignition.", "unit": "mg/l"},
        {"id": "TRANS", "name": "Transparency", "description": "Measure of the depth of light penetration into the water.", "unit": "m"},
        {"id": "TURB", "name": "Turbidity", "description": "Cloudiness or haziness of a fluid caused by suspended solids that are usually invisible to the naked eye.", "unit": "mg/l"},
        {"id": "TEMP", "name": "Temperature", "description": "Ambient temperature of the water.", "unit": "°C"},
        {"id": "pH", "name": "pH", "description": "The negative logarithm of the hydrogen ion concentration, a measure of acidity or alkalinity of water soluble substances.", "unit": "numeric"},
    ]

    for var_data in variables_data:
        variable = db.query(models.Variable).filter(models.Variable.id == var_data["id"]).first()
        if not variable:
            variable = models.Variable(**var_data)
            db.add(variable)
    db.commit()
