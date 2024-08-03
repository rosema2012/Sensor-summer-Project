using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class RadarDisplay : MonoBehaviour
{
    public Transform vrCamera;  // Asegúrate de asignar esto en el Inspector
    public List<Vector3> points = new List<Vector3>();
    public float radarRadius = 100f;  // El radio visual del radar en la GUI
    public float maxDistance = 8f; // Máxima distancia del radar en metros en el mundo real
    private Texture2D blackTexture, whiteTexture, greenTexture, yellowTexture, redTexture;

    private void Start()
    {
        // Crear una textura negra de 1x1 píxel
        blackTexture = new Texture2D(1, 1);
        blackTexture.SetPixel(0, 0, Color.black);
        blackTexture.Apply();

        // Crear una textura blanca de 1x1 píxel para puntos y líneas
        whiteTexture = new Texture2D(1, 1);
        whiteTexture.SetPixel(0, 0, Color.white);
        whiteTexture.Apply();

        // Crear texturas de colores para los anillos
        greenTexture = CreateTexture(Color.green);
        yellowTexture = CreateTexture(Color.yellow);
        redTexture = CreateTexture(Color.red);

        GenerateRandomPoints(); // Genera puntos aleatorios al iniciar
    }

    private Texture2D CreateTexture(Color color)
    {
        Texture2D texture = new Texture2D(1, 1);
        texture.SetPixel(0, 0, color);
        texture.Apply();
        return texture;
    }

    private void OnGUI()
    {
        DrawRadarBackground();
        DrawRadarRings();
        DrawRadarCross();
        DrawRadarPoints();
    }

    private void DrawRadarBackground()
    {
        // Dibujar fondo del radar con una textura negra opaca
        GUI.color = Color.black;
        GUI.DrawTexture(new Rect(10, Screen.height - 230, 220, 220), blackTexture, ScaleMode.StretchToFill);
    }

    private void DrawRadarRings()
    {
        float[] ringDistances = { 0.25f, 0.50f, 0.75f, 1.0f }; // Porcentajes del radarRadius
        Texture2D[] ringColors = { whiteTexture, greenTexture, yellowTexture, redTexture };

        for (int i = 0; i < ringDistances.Length; i++)
        {
            float radius = radarRadius * ringDistances[i];
            DrawRing(radius, ringColors[i]);
        }
    }

    private void DrawRing(float radius, Texture2D texture)
    {
        Vector2 center = new Vector2(10 + 110, Screen.height - 230 + 110);
        float thickness = 2;  // Grosor de la línea del anillo
        int segments = 360;   // Número de segmentos para formar el anillo

        GUI.color = texture.GetPixel(0, 0);
        for (int i = 0; i < segments; i++)
        {
            float angle = i * Mathf.Deg2Rad * 360 / segments;
            float x = center.x + Mathf.Sin(angle) * radius;
            float y = center.y + Mathf.Cos(angle) * radius;
            GUI.DrawTexture(new Rect(x - thickness / 2, y - thickness / 2, thickness, thickness), texture, ScaleMode.StretchToFill);
        }
    }

    private void DrawRadarCross()
    {
        // Dibujar líneas de cruz blanca en el radar
        GUI.color = Color.white;
        GUI.DrawTexture(new Rect(120 + 0, Screen.height - 230, 2, 220), whiteTexture, ScaleMode.StretchToFill); // Línea vertical
        GUI.DrawTexture(new Rect(10, Screen.height - 120, 220, 2), whiteTexture, ScaleMode.StretchToFill); // Línea horizontal
    }

    private void GenerateRandomPoints()
    {
        points.Clear(); // Limpiar la lista de puntos antes de generar nuevos
        for (int i = 0; i < 10; i++) // Generar 10 puntos aleatorios
        {
            Vector3 randomPoint = new Vector3(Random.Range(-maxDistance, maxDistance), 0, Random.Range(-maxDistance, maxDistance));
            points.Add(randomPoint);
        }
    }

    private void DrawRadarPoints()
    {
        foreach (Vector3 point in points)
        {
            DrawRadarPoint(point);
        }
    }

    private void DrawRadarPoint(Vector3 point)
    {
        // Asegurar que la cámara VR está asignada
        if (vrCamera == null)
        {
            Debug.LogError("vrCamera no está asignada.");
            return;
        }

        Vector3 direction = point - vrCamera.position;
        float distance = direction.magnitude;

        if (distance <= maxDistance)
        {
            // Calcular la distancia y el ángulo para el radar
            float scaledDistance = (distance / maxDistance) * radarRadius;
            float angle = Mathf.Atan2(direction.x, direction.z) * Mathf.Rad2Deg - vrCamera.eulerAngles.y;

            float centerX = 10 + 110; // 10 es el margen izquierdo, 110 es la mitad de la anchura del radar
            float centerY = Screen.height - 230 + 110; // 230 es el margen desde la parte superior, 110 es la mitad de la altura del radar

            float x = centerX + Mathf.Sin(angle * Mathf.Deg2Rad) * scaledDistance;
            float y = centerY - Mathf.Cos(angle * Mathf.Deg2Rad) * scaledDistance;

            // Determinar el color del punto según el círculo en el que se encuentra
            Color pointColor;
            if (scaledDistance <= radarRadius * 0.25f)
            {
                pointColor = Color.white;
            }
            else if (scaledDistance <= radarRadius * 0.50f)
            {
                pointColor = Color.green;
            }
            else if (scaledDistance <= radarRadius * 0.75f)
            {
                pointColor = Color.yellow;
            }
            else
            {
                pointColor = Color.red;
            }

            GUI.color = pointColor;
            GUI.DrawTexture(new Rect(x - 5, y - 5, 10, 10), whiteTexture, ScaleMode.StretchToFill);
        }
    }
}
