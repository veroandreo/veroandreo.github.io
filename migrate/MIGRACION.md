# Migración Hugo/Wowchemy → Quarto

Registro de qué se migró, cómo y qué quedó pendiente. Para usar el sitio en el
día a día, ver el `README.md` de la raíz.

Estado al 3 de septiembre de 2026, con el sitio ya publicado en
<https://veroandreo.github.io>. Nada del sitio Hugo fue modificado ni borrado:
vive todavía en el repo de GitLab, con `content/`, `config/` y `static/` intactos.

## Qué hay acá

```
quarto-site/
├── _quarto.yml            config del sitio, navbar, footer, tema
├── index.qmd              home: hero con la bio, Interests, Skills,
│                          publicaciones, Experience y Contact
├── publications/          52 publicaciones + listing en grilla
├── posts/                 5 posts + listing
├── talks/                 5 charlas/talleres + listing
├── courses/index.qmd      la lista de cursos y talleres
├── assets/                tema scss, imágenes, logos, cv.pdf, academicons
├── _extensions/           extensión academicons
└── migrate/
    ├── migrate_v2.py                   el script de migración
    ├── migrate_hugo_to_quarto_v1.py    el original, como referencia
    ├── mapa_categorias.py              vocabulario de categorías
    ├── aplicar_categorias.py           aplica ese vocabulario a los .qmd
    ├── italicas_especies.py            itálicas de nombres científicos
    ├── about-old.qmd                   la página About retirada (no se renderiza)
    └── MIGRACION.md                    este archivo
```

Reproducir la migración desde cero:

```bash
cd quarto-site
python3 migrate/migrate_v2.py --hugo ../../content --quarto . --static ../../static
quarto render
```

## Evaluación del script v1

El script anterior servía de esqueleto — el recorrido de secciones, la detección
de page bundles y el armado de links estaban bien — pero contra el contenido real
de este repo tenía cinco agujeros, tres de ellos graves:

| # | Problema | Alcance |
|---|---|---|
| 1 | **TOML leído con un regex `key = "value"`.** Los arrays se perdían: `authors`, `tags`, `publication_types`, `projects`. | **51 de 52 publicaciones** quedaban sin autores, sin categorías y sin tipo |
| 2 | **Fechas RFC 1123 sin convertir** (`Wed, 30 Dec 2020 00:00:00 +0000`). Quarto no las ordena ni las formatea. | los 5 posts |
| 3 | **Valores YAML multilínea truncados** a la primera línea (el parser solo miraba la línea de la clave). | los abstract de las 5 charlas |
| 4 | **Archivos sueltos tratados como bundle**: para un `.md` suelto tomaba `content/publication/` entera como carpeta de assets, y buscaba ahí el `featured.png`. | las 51 publicaciones sueltas |
| 5 | **Secciones enteras sin migrar**: `courses/_index.md`, el widget de experiencia, la bio completa (educación, intereses, organizaciones, redes) y `static/`. | páginas About, Courses y CV |

Además, los shortcodes `{{% callout %}}` quedaban tal cual, y los links iban al
front matter en un campo `links:` que Quarto no renderiza.

## Qué hace la v2

- TOML con **`tomllib`** (stdlib desde Python 3.11) y YAML con **PyYAML**. Adiós a
  los parsers a mano; los dos formatos entran completos, arrays incluidos.
- Fechas normalizadas a `YYYY-MM-DD` (ISO, RFC 1123 y `...T00:00:00Z`).
- Los abstract vacíos de front matter pasan al **cuerpo** del qmd, con los links
  arriba como una línea de markdown (así se ven de verdad) y una sección
  `## Citation` armada con autores, año y revista.
- `{{% callout note %}}` → `::: {.callout-note}`. Los `{{< ref >}}` y
  `{{< gallery >}}` que quedan se avisan por consola.
- Slugs normalizados (`2009-01-01_Environmental_factor` → `2009-01-01-environmental-factor`).
- Lee `[header] image` del front matter de Hugo, que Wowchemy v5 no renderizaba.
- Migra About (bio + intereses + educación + experiencia + contacto), Courses,
  el avatar y los archivos de `static/`.
- Descarta los links "Follow" a Twitter que traían las charlas.
- Normaliza ```` ```shell script ```` → ```` ```bash ````: con el lenguaje de dos
  palabras Pandoc no abre el bloque como código, y el post de *i.landsat*
  renderizaba los comentarios `#` de adentro como títulos de sección.
- Al final imprime un resumen con los avisos que hay que revisar a mano.

Resultado: **64 elementos** migrados, **68 páginas** renderizadas sin errores.

## Trabajo posterior a la migración

Todo esto se hizo después de la primera pasada y ya está aplicado.

### Imágenes de las publicaciones

Las URLs estaban en `[header] image` del Hugo y nunca se habían visto porque
Wowchemy v5 no renderiza ese campo. De las 12 declaradas:

- **8 se bajaron** a la carpeta de cada publicación como `featured.jpg` / `.png`
  y se redimensionaron a 1400 px de ancho (la de PLOS pesaba 4,4 MB; la de
  IGARSS, 3,7 MB).
- **1** sale de `assets/img/headers/quintana2026-jme-fig8.png`.
- **3 quedaron con el placeholder**: MDPI y Wiley bloquean la descarga automática
  y el hotlink tampoco carga en el navegador. Hay que bajarlas a mano y ponerlas
  como `featured.jpg` en su carpeta:
  `2023-07-11-risk-stratification-tartagal`, `2026-07-08-mtct-gran-chaco`,
  `2024-01-27-remote-sensing-and-biodiversity`.
- **Falta una**: `2025-12-01-aedestraits`. La URL de Hugo apunta a una página de
  Nature, no a una figura.

Las 40 restantes usan `assets/img/headers/landsatlooks.jpg` como placeholder.

### Categorías

De **124 etiquetas distintas a 38**, y de 85 usadas una sola vez a 4. En tres pasos:
primera palabra en mayúscula, acrónimo junto a su expansión, y las de un solo uso
plegadas a una categoría más general.

Decisiones tomadas: se eliminaron **Cholera, Malaria, SDG**, los tres **lugares**
(Argentina, South America, Europe) y **FOSS4G, GDAL, R, Tutorial, Workshop** — al
borrar FOSS4G se fueron con ella `open source`, `OSGeo`, `Open Data`,
`Operative systems`, `operational` y `software development`. **GRASS GIS** pasó a
llamarse **GRASS** y absorbió `TGRASS`, `add-on` y `pymodis`.

El vocabulario vive en `mapa_categorias.py` y se aplica con:

```bash
python3 migrate/aplicar_categorias.py --dry-run   # simula
python3 migrate/aplicar_categorias.py             # escribe
```

Relee los `.qmd` en cada corrida, así que no se desincroniza si se editan a mano.

### Itálicas de nombres científicos

75 nombres en 27 archivos, en títulos y abstracts, con
`migrate/italicas_especies.py`. La lista está curada a mano (25 binomios y 16
géneros) porque la detección automática por patrón "Género especie" devolvía
basura como "Journal article".

Dos casos deliberados:

- **`Rosa` sola no se italiza**: colisiona con R. Rosa, coautora en tres papers.
  Solo se marca dentro del binomio *Rosa rubiginosa*.
- **Los virus quedaron en redonda.** Por ICTV el género *Orthohantavirus* iría en
  itálica, pero en los títulos publicados está en redonda y el uso vernáculo
  ("Andes virus") no se italiza. Sin decidir.

Lo que **no** cubre: el texto de las categorías. La categoría "Aedes aegypti"
sigue en redonda porque Quarto renderiza el texto del tag literal, sin markdown.
Haría falta un poco de JS.

### Iconos

- **Font Awesome 6.7.2** desde cdnjs, en `include-in-header`.
- **academicons** como extensión (`quarto add schochastics/academicons`) para
  ORCID, Scholar, ResearchGate y Overleaf. La extensión solo inyecta su CSS en
  las páginas que usan el shortcode `{{< ai ... >}}`, y el footer está en todas,
  así que la hoja y las tipografías se copiaron también a `assets/academicons/`
  y se cargan desde `include-in-header`.

### Estructura de las páginas

La primera pasada dejó la bio en una página About aparte y un home sin biografía.
El 2 de septiembre eso se revirtió, para volver a la estructura que tenía el sitio
Hugo, donde el widget `about` era el segundo bloque de la home y no había página
About:

- **No hay página About.** El archivo quedó guardado en `migrate/about-old.qmd`,
  fuera del render, y About salió de la navbar.
- El **home** tiene: hero con la bio, Interests, Skills, Recent publications
  (6, dos filas), Experience y Contact. El listado de posts sigue fuera.
- **Skills e Interests** volvieron al home. **Education** no: ya está en el CV, y
  Skills e Interests duplicaban lo que dice la bio. Sigue en `about-old.qmd`.
- El bloque `about:` del home usa **`id: hero`** para que se lleve solo el hero.
  Sin eso se traga el cuerpo entero de la página (ver Aprendizajes).

### Bio, Interests y favicon

- La **bio se reescribió** alrededor de una sola pregunta — *where and when do
  environmental conditions converge to make a disease outbreak likely?* — y
  después el cómo (Earth observation, series de tiempo, estadística
  espacio-temporal y machine learning, forecasts y mapas de riesgo) y el open
  source. Vocabulario preferido: **Earth observation** antes que "remote sensing",
  *satellite image time series*, *spatio-temporal modeling*, *forecasting*,
  *risk mapping*. **Sin el marco "One Health"**, decisión explícita de Vero.
- **Interests dejó de ser una lista plana** y pasó a tres grupos en columnas
  (*What I study* / *Data I work with* / *How I work*), porque la lista mezclaba
  preguntas, datos y herramientas en un mismo nivel.
- La línea mono debajo del nombre lleva la **afiliación**, no una lista de temas.
- **Favicon**: `assets/img/favicon.png`, redimensionado a 192 px desde
  `assets/media/icon.png` del sitio Hugo (`../../assets/media/icon.png` desde acá),
  que es el mismo archivo del que Wowchemy generaba sus favicons. Se declara con
  `favicon:` en `_quarto.yml`.
- Se achicó el aire entre secciones del home y se sacó el filete al pie del hero:
  el `h2.section-label` de la sección siguiente ya trae el suyo y quedaban dos
  líneas seguidas.

## Lo que quedó pendiente

1. **Las tres imágenes de MDPI y Wiley**, más la de AedesTraits (arriba).
2. **Las URLs cambian.** Antes `/publication/2009-01-01_Environmental_factor/`,
   ahora `/publications/2009-01-01-environmental-factor/`. Como además cambia el
   dominio (GitLab → GitHub Pages), hay que actualizar ORCID, Scholar y
   ResearchGate. Si querés conservar las viejas, Quarto soporta `aliases:` en el
   front matter.
3. **Un autor quedó como una sola cadena**: en `talks/ogh2019-grass-intro` el
   Hugo decía `authors: [Veronica Andreo and Markus Neteler]`, un solo elemento.
4. **`{{< gallery >}}`** de `content/home/gallery/` no se migró: era un widget de
   la home de Wowchemy que hoy no tiene lugar en la estructura nueva.
5. ~~**El workflow de deploy**~~ **Resuelto el 3/9/2026.** El repo
   `veroandreo/veroandreo.github.io` existe, la versión de Quarto quedó fijada en
   `1.7.31` y el sitio se publica solo en cada push a `main`. Ver "Publicación"
   más abajo.
6. **Modo oscuro**: fuera. El `_quarto.yml` declara un solo tema claro.
7. **`index.qmd` está escrito a mano**, y bastante reescrito respecto de lo que
   generó el script. Si volvés a correr `migrate_v2.py`, `migrate_about` vuelve a
   crear `about/index.qmd` y con eso reaparece la página About que se retiró:
   comentá esa llamada, o borrá la carpeta después de correrlo y acordate de sacar
   About de la navbar otra vez.
8. **Experience está en el home, escrito a mano**, no sale de
   `content/home/experience.md`. Si agregás un puesto hay que editarlo ahí.
9. **Logos de las instituciones**: `assets/img/logos/` tiene CONICET (Wikimedia
   Commons, CC BY 2.5 AR), Universidad de Twente (dominio público) y NC State. El
   de Twente que está en uso mide 46×17 px: se ve blando en pantallas retina,
   conviene reemplazarlo por un SVG o un PNG de ~200 px de ancho.
10. **Categorías**: quedaron 38 y el objetivo era menos. Con un corte de "mínimo
    3 usos" quedarían 27; con "mínimo 4", 20.

## Publicación

El sitio vive en `veroandreo/veroandreo.github.io` y se publica en
<https://veroandreo.github.io>. El flujo es: push a `main` → GitHub Actions
renderiza con Quarto 1.7.31 → `quarto publish gh-pages` empuja el HTML a la rama
`gh-pages` → GitHub Pages sirve esa rama. **No hay que renderizar ni commitear
`_site/` a mano**: está en el `.gitignore` a propósito.

Dos cosas que hubo que resolver en el primer deploy y que no son obvias:

**`quarto publish gh-pages` en CI sabe actualizar la rama, no crearla.** El primer
run falla con *"the remote origin does not have a branch named gh-pages"*. Hay que
sembrarla una vez a mano, con una rama huérfana que sólo tenga un `.nojekyll`:

```bash
git checkout --orphan gh-pages
git rm -rq --cached .
touch .nojekyll && git add .nojekyll
git commit -m "Seed gh-pages branch"
git push -u origin gh-pages
git checkout -f main      # el -f hace falta: el rm --cached dejó todo untracked
```

**En un repo `usuario.github.io`, GitHub activa Pages solo, apuntando a `main`.**
Eso sirve el `README.md` renderizado por Jekyll en vez del sitio. Hay que mover la
fuente a `gh-pages`:

```bash
gh api -X PUT repos/veroandreo/veroandreo.github.io/pages \
  -f 'source[branch]=gh-pages' -f 'source[path]=/'
gh api -X POST repos/veroandreo/veroandreo.github.io/pages/builds   # empujón
```

## Aprendizajes de Quarto

Cosas que costaron tiempo y conviene tener a mano.

**El bloque `about:` se traga el cuerpo de la página.** Con `template: solana` o
`trestles`, todo el contenido del documento entra dentro del bloque. En el home
eso hacía que la foto se centrara verticalmente contra las tarjetas de
publicaciones y que el margen del hero no separara nada. La solución es
`about: { id: hero }` y envolver **solo** el hero en `::: {#hero} ... :::`; el
resto del documento queda por fuera, en el flujo normal.

**Una listing declarada en el front matter se renderiza aunque no exista su div.**
Si sacás el `::: {#latest-posts} :::` del cuerpo pero dejás el `- id: latest-posts`
en el YAML, Quarto cuelga el listado al final de la página. Para sacarlo hay que
borrar las dos cosas.

**La especificidad de Quarto le gana al orden del archivo.** Quarto escribe
selectores como `div.quarto-about-solana .about-entity .about-link` (0,3,1); una
regla propia de una sola clase pierde por más abajo que esté en el `.scss`. Las
reglas de este tema que tocan el bloque `about`, las tarjetas de listado o las
categorías están escritas con la misma profundidad a propósito. **Verificar que
una regla está en el CSS compilado no alcanza**: hay que comprobar cuál gana.

**`image-shape: round` sobre una imagen no cuadrada da una elipse.** Quarto
aplica `border-radius: 50 %`, no un recorte: si la imagen no es cuadrada, sale un
óvalo. Para la caricatura, que es 2:3, va `rounded`.

**Al apilar en móvil, `column` no es lo contrario de `row-reverse`.** El hero
invierte la fila por CSS para dejar la foto a la izquierda; el media query de
pantallas chicas decía `flex-direction: column`, que vuelve al orden del DOM y
mandaba la foto **abajo de toda la bio**. Con el hero corto casi no se notaba.
Lo correcto es `column-reverse`.

**Un `integrity` mal puesto rompe la hoja en silencio.** Los iconos de Font
Awesome no se veían porque el `<link>` llevaba un hash SRI inventado; el navegador
descarta la hoja sin avisar. Si un CSS de CDN "no hace nada", mirar eso primero.
