### Sistema para la captura de datos de usuarios e inventario de red de una empresa de gestión de la red de distribución de agua potable
### System for sensoring users’ data and inventorying the network of a potable water distribution management company

---

Autores:
- Francisco Martínez Esteso

Tutores: 
- Elena María Navarro Martínez
- Juan Peralta Malvar

--- 

Los Sistemas de Información Geográfica (SIG) se han convertido en una herramienta fundamental en el día a día de un profesional de las tecnologías de la información enrolado en el área del geoprocesamiento, pero también se hacen imprescindibles en otros campos profesionales como son la cartografía, la agricultura y el sector transporte, entre otros muchos. También cada día son más las empresas que deciden embarcarse en proyectos de Transformación Digital de sus organizaciones, buscando incrementar la productividad y eficiencia de sus compañías a través del uso de las tecnologías SIG. Para ello crean diferentes tipos de infraestructuras que buscan mejorar las capacidades geoespaciales de la empresa en diferentes aspectos como, por ejemplo, la mejora de las interacciones entre clientes y usuarios. El aumento de la automatización en los procesos empresariales y el auge de las nuevas técnicas de inteligencia artificial han permitido a los Sistemas de Información Geográfica enfrentarse a nuevos retos, trabajando en áreas donde nunca antes había tenido cabida este tipo de sistemas. A todo ello se añade la mejora de los SIG con respecto al análisis de datos y exploración de patrones de la información geográfica.
Este proyecto muestra el proceso de desarrollo llevado a cabo en un proyecto SIG real, en el que se realiza un proceso de catastro técnico y comercial para una empresa de aguas peruana ubicada en la ciudad de Chimbote. El proyecto se ha llevado a cabo íntegramente en el seno de una empresa española, Eptisa, con amplia experiencia en trabajos relacionados con la información geográfica tanto en España como en el resto del mundo.
En esta memoria se documentan los trabajos llevados a cabo en colaboración con un equipo de profesionales internacionales, cuyo fin es la codificación de una cartografía mediante la ejecución de procesos automáticos en segundo plano y la creación de un sistema de clasificación de elementos cartográficos que da apoyo al equipo técnico en las tareas de digitalización de las parcelas catastrales de la cartografía base. Además, el proyecto termina resaltando la necesidad de crear diferentes herramientas de gestión y tratamiento geográfico de datos para la remodelación de diferentes elementos de la cartografía.

--- 

- anexo_1:
    - Remodelar Lotes.pyt
- capitulo_3:
    - config.txt
    - constants.py
    - tecnico_CodificarLotes.py
    - tecnico_CodificarManzanas.py
    - tecnico_CodificarSubSectores.py
    - tecnico_NumerarManzanas.py
    - tecnico_NumerarEsquinas.py
    - tecnico_NumerarLotes.py
    - utilities.py
- capitulo_4:
    - bbdd:
        - bbdd_creater_script.txt
    - version_cartografia_base_v1.gdb
    - blocks_details_v2.csv
    - blocks_details_v3_results.csv
    - spider_database_data.py
    - spider_kmeans_results.py