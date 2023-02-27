import requests
import pubchempy
import logging


_logger = logging.getLogger("molecalc:calc_views")

CACTUS = 'https://cactus.nci.nih.gov/chemical/structure/{0}/{1}'

# TODO Write a function that tries pubchempy first and falls back to NCI Cactus
# if that fails; make sure it defaults to SMILES if both fail

def smiles_to_iupac_pubchempy(smiles):
    compounds = pubchempy.get_compounds(smiles, namespace='smiles')
    match = compounds[0]
    return match.iupac_name


def smiles_to_iupac_cactus(smiles):
    url = CACTUS.format(smiles, "iupac_name")
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def smiles_to_iupac(smiles):
    try:
        name = smiles_to_iupac_pubchempy(smiles)
        if name is None:
            raise TypeError
        return name
    except Exception(e):
        _logger.info(f'Attempting IUPAC name search with pubchempy resulted\n'  \
                       ' in Exception {e}')
        pass

    try:
        name = smiles_to_iupac_cactus(smiles)
        if name is None:
            raise TypeError
        return name
    except Exception(e):
        _logger.info(f'Attempting IUPAC name search with CACTUS NIC resulted\n' \
                     ' in Exception {e}')

    _logger.info(f'Attempting IUPAC name search failed; returning SMILES')
    return smiles
