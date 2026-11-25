# # ------------------------------------------------------------------------------
# # 5.3. Especialització funcional - Dominància i diversitat funcional
# # ------------------------------------------------------------------------------

# ## Districtes
# resultats_especialitzacio_districtes = especialitzacio.analisi_especialitzacio(
#     zones=districtes_base,
#     edificis=edificis_base,
#     idx_zones=dict_indexs["Limits_administratius"]["Districtes"],
#     usos_exclosos=["1_residential", "2_agriculture"]
# )
# # Addició dels camps d'especialització
# districtes_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
#     zones=districtes_base,
#     resultats=resultats_especialitzacio_districtes
# )

# ## Barris
# resultats_especialitzacio_barris = especialitzacio.analisi_especialitzacio(
#     zones=barris_base,
#     edificis=edificis_base,
#     idx_zones=dict_indexs["Limits_administratius"]["Barris"],
#     usos_exclosos=["1_residential", "2_agriculture"]
# )
# # Addició dels camps d'especialització
# barris_especialitzacio = especialitzacio.afegir_resultats_especialitzacio(
#     zones=barris_base,
#     resultats=resultats_especialitzacio_barris
# )

# # Assignar els camps d'especialització a la malla a partir dels edificis
# malla_especialitzacio = especialitzacio.assignar_especialitzacio_per_hexagons(
#     edificis=edificis_base,
#     malla=malla_base,
#     usos_exclosos=['1_residential', "2_agriculture"]
# )

# # ------------------------------------------------------------------------------
# # 5.4. Anàlisi bivariant dominància i diversitat funcional
# # ------------------------------------------------------------------------------

# malla_especialitzacio_bivariantDDF = especialitzacio.afegir_classe_bivariant_DF_D(
#     layer=malla_especialitzacio
# )

# # ------------------------------------------------------------------------------
# # 5.5. Anàlisi bivariant
# # ------------------------------------------------------------------------------

# ## Districtes
# districtes_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
#     layer=districtes_especialitzacio
# )

# ## Barris
# barris_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
#     layer=barris_especialitzacio
# )

# ## Malla hexagonal
# malla_bivariant_DF_A = especialitzacio.afegir_classe_bivariant_DF_A(
#     layer=malla_accessibilitat
# )

# # Separar els hexàgons vàlids dels no vàlids - aquells amb el camp
# # de l'anàlisi bivariant NULL
# hexagons_valids_DF_A, hexagons_no_valids_DF_A = hexagons.separar_hexagons_valids(
#     malla=malla_bivariant_DF_A
# )


# # ------------------------------------------------------------------------------
# # 6.3. Especialització funcional - Dominància / Diversitat funcional
# # ------------------------------------------------------------------------------

# # Omissió dels usos residencial i agricultura

# ## Districtes
# layers_simbologia_especialitzacio_districtes = simbologia_general.simbologia_especialitzacio_funcional(
#     zones=districtes_especialitzacio,
#     ua="Districtes"
# )

# ## Barris
# layers_simbologia_especialitzacio_barris = simbologia_general.simbologia_especialitzacio_funcional(
#     zones=barris_especialitzacio,
#     ua="Barris"
# )

# ## Malla hexagonal
# layers_simbologia_especialitzacio_hexagons = simbologia_general.simbologia_hexagons_especialitzacio_funcional(
#     hexagons=malla_especialitzacio_bivariantDDF,
#     terme=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
# )

 # ------------------------------------------------------------------------------
# # 6.4. Anàlisi bivariant Diversitat funcional - Accessibilitat
# # ------------------------------------------------------------------------------

# ## Malla hexagonal - hexàgons vàlids
# layers_simbologia_bivariant_valids = simbologia_general.simbologia_hexagons_especialitzacio_funcional(
#     hexagons=hexagons_valids_DF_A
# )

# ## Malla hexagonal - hexàgons no vàlids
# layer_simbologia_bivariant_no_valids = simbologies.simbologia_unica(
#     layer=hexagons_no_valids_DF_A,
#     **config.SIMBOLOGIA["Hexagons_no_valids"]
# )

# # ------------------------------------------------------------------------------
# # 7.4. Composicions especialització funcional
# # ------------------------------------------------------------------------------

# layout_especialitzacio.composicio_especialitzacio(
#     capes=layers_simbologia_especialitzacio_hexagons["hexagons"],
#     capa_terme=layers_simbologia_especialitzacio_hexagons["terme_municipal"],
#     capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"]
# )

# # ------------------------------------------------------------------------------
# # 7.6. Composició anàlisi bivariant
# # ------------------------------------------------------------------------------

# ## Malla hexagonal
# layout_bivariant_zones.composicio_bivariant_zones(
#     zona="Hexagons",
#     districtes=districtes_base,
#     capes=[
#         layers_simbologia_bivariant_valids["bivariant"],
#         layer_simbologia_bivariant_no_valids
#     ],
#     capa_extent=dict_layers_clean["Limits_administratius"]["TermeMunicipal"],
#     amb_capçalera=False
# )