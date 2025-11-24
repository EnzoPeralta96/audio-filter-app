# Guía de Deployment Online

Esta guía te ayudará a publicar tu aplicación en internet **GRATIS**.

## ¿Necesito instalar FFmpeg en mi PC?

**Para desarrollo local**: Sí, necesitas FFmpeg en tu PC.

**Para producción (deploy online)**: NO. FFmpeg se instala automáticamente en el servidor. Los usuarios solo necesitan un navegador.

---

## 🚀 Opción 1: Railway (La más fácil)

### Paso 1: Preparar repositorio en GitHub

1. Crea un repositorio en GitHub
2. Sube todos los archivos de tu proyecto:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
   git push -u origin main
   ```

### Paso 2: Deploy en Railway

1. Ve a https://railway.app
2. Haz clic en "Start a New Project"
3. Selecciona "Deploy from GitHub repo"
4. Conecta tu cuenta de GitHub
5. Selecciona tu repositorio
6. Railway detectará automáticamente `railway.json` y `nixpacks.toml`
7. Espera a que termine el build (2-3 minutos)
8. Railway te dará una URL pública: `tu-app.railway.app`

**¡Listo!** Tu app está online.

---

## 🎨 Opción 2: Render

### Paso 1: Sube tu código a GitHub (igual que Railway)

### Paso 2: Deploy en Render

1. Ve a https://render.com
2. Crea una cuenta
3. Haz clic en "New +" → "Web Service"
4. Conecta tu repositorio de GitHub
5. Render detectará automáticamente `render.yaml`
6. Haz clic en "Create Web Service"
7. Espera el build (3-5 minutos)
8. Render te dará una URL: `tu-app.onrender.com`

**¡Listo!** Tu app está online.

---

## 🐳 Opción 3: Docker (Más técnico)

Si quieres usar Docker en cualquier plataforma:

```bash
# 1. Construir imagen
docker build -t audio-filter-app .

# 2. Ejecutar localmente
docker run -p 8000:8000 audio-filter-app

# 3. Acceder en: http://localhost:8000
```

Para subir a Docker Hub y deployar en cualquier servidor:

```bash
# Subir a Docker Hub
docker tag audio-filter-app TU_USUARIO/audio-filter-app
docker push TU_USUARIO/audio-filter-app

# En el servidor (DigitalOcean, AWS, etc.)
docker pull TU_USUARIO/audio-filter-app
docker run -d -p 80:8000 TU_USUARIO/audio-filter-app
```

---

## ⚙️ Archivos de Configuración Incluidos

Ya he creado estos archivos para que el deployment sea automático:

- `Dockerfile` - Para Docker
- `railway.json` - Para Railway
- `nixpacks.toml` - Para Railway (instala FFmpeg)
- `render.yaml` - Para Render
- `.gitignore` - Para Git

**No necesitas modificar nada**, solo sube tu código a GitHub y selecciona la plataforma.

---

## 📋 Checklist antes de Deploy

- [ ] Código subido a GitHub
- [ ] Archivo `requirements.txt` incluido
- [ ] Archivos de configuración incluidos (Dockerfile, railway.json, etc.)
- [ ] El archivo `.gitignore` evita subir archivos temporales
- [ ] Probado localmente con `python main.py`

---

## 🎯 Recomendación

**Para estudiantes/proyectos académicos**: Usa **Railway** o **Render**. Son las opciones más simples y gratuitas.

**Para producción profesional**: Usa **Docker** + servidor cloud (AWS, DigitalOcean, etc.)

---

## 🆘 Problemas Comunes

### Error: "FFmpeg not found"

**Solución**: Asegúrate de que los archivos `nixpacks.toml` o `render.yaml` están en tu repositorio. Estos archivos instalan FFmpeg automáticamente.

### Error: "Port already in use"

**Solución**: El código ya está configurado para usar la variable `PORT` del entorno. No necesitas cambiar nada.

### Error en Railway/Render: "Build failed"

**Solución**:
1. Verifica que `requirements.txt` está en la raíz del proyecto
2. Verifica que todos los archivos están en GitHub
3. Revisa los logs del build en la plataforma

---

## 📊 Límites de las versiones gratuitas

| Plataforma | Límite Mensual | Build Time | Uptime |
|------------|----------------|------------|---------|
| Railway    | 500 horas      | ~2-3 min   | 24/7    |
| Render     | 750 horas      | ~3-5 min   | 24/7    |

Ambas son más que suficientes para un proyecto académico.

---

## 🎓 Para tu presentación

Una vez desplegado, puedes:

1. Compartir la URL pública con tus compañeros
2. Demostrar en vivo sin instalar nada
3. Mostrar el código en GitHub
4. Explicar la arquitectura cloud

¡Buena suerte con tu proyecto!
