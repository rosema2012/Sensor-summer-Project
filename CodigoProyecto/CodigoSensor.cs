using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class EcolocalizationSimulation : MonoBehaviour
{
    public GameObject personPrefab;
    public int numberOfPoints = 10;
    public Transform vrCamera; // Cámara VR para orientación
    public RadarDisplay radarDisplay; // Referencia al script RadarDisplay
    public Material outlineMaterial; // Material con el shader de contorno

    private BoxCollider sensorArea;
    private List<Vector3> sensorData;
    private List<GameObject> personObjects; // Lista de los objetos person

    void Start()
    {
        // Verificar que radarDisplay no sea nulo
        if (radarDisplay == null)
        {
            Debug.LogError("RadarDisplay no asignado en el Inspector.");
            return;
        }

        // Obtener el BoxCollider del área del sensor
        sensorArea = GetComponent<BoxCollider>();
        if (sensorArea == null)
        {
            Debug.LogError("No BoxCollider found on the SensorArea GameObject.");
            return;
        }

        sensorData = GenerateSensorData();
        radarDisplay.points = sensorData; // Asignar los puntos al radar display

        personObjects = new List<GameObject>(); // Inicializar la lista de objetos person

        foreach (Vector3 point in sensorData)
        {
            GameObject person = CreatePersonAtPoint(point);
            personObjects.Add(person); // Agregar el objeto person a la lista
        }
    }

    List<Vector3> GenerateSensorData()
    {
        List<Vector3> data = new List<Vector3>();
        Vector3 center = sensorArea.transform.position;
        Vector3 size = sensorArea.size;
        for (int i = 0; i < numberOfPoints; i++)
        {
            Vector3 randomPoint = center + new Vector3(
                Random.Range(-size.x / 2, size.x / 2),
                0.5f, // Altura fija
                Random.Range(-size.z / 2, size.z / 2)
            );
            data.Add(randomPoint);
        }
        return data;
    }

    GameObject CreatePersonAtPoint(Vector3 point)
    {
        GameObject person = Instantiate(personPrefab, point, Quaternion.identity);
        Debug.Log($"Created person at {point}");

        // Crear un GameObject vacío para el contorno de wireframe
        GameObject wireframeCube = new GameObject("WireframeCube");
        wireframeCube.transform.position = point + new Vector3(0, 1, 0); // Ajustar la altura según sea necesario
        wireframeCube.transform.localScale = new Vector3(1, 2, 1); // Ajustar el tamaño del cubo
        wireframeCube.transform.parent = person.transform; // Hacer que el contorno sea hijo del soldado

        // Añadir el componente WireframeCube
        WireframeCube wfCube = wireframeCube.AddComponent<WireframeCube>();

        // Usar una corrutina para esperar hasta el siguiente frame antes de asignar el material
        StartCoroutine(AssignMaterialNextFrame(wfCube));

        return person; // Retornar el objeto person
    }

    IEnumerator AssignMaterialNextFrame(WireframeCube wfCube)
    {
        // Esperar hasta el siguiente frame
        yield return null;

        Renderer renderer = wfCube.GetComponent<Renderer>();
        if (renderer != null)
        {
            renderer.material = outlineMaterial;
        }
        else
        {
            Debug.LogError("Renderer not found on WireframeCube");
        }
    }

    void Update()
    {
        if (vrCamera == null)
        {
            Debug.LogWarning("vrCamera no está asignada en el Inspector.");
            return;
        }

        foreach (GameObject person in personObjects)
        {
            Renderer renderer = person.GetComponentInChildren<WireframeCube>()?.GetComponent<Renderer>();
            if (renderer != null)
            {
                float distance = Vector3.Distance(person.transform.position, vrCamera.position);
                UpdateColorByDistance(renderer, distance);
            }
        }
    }

    void UpdateColorByDistance(Renderer renderer, float distance)
    {
        // Ajustar el color basado en la distancia
        if (distance <= radarDisplay.maxDistance * 0.25f)
        {
            renderer.material.SetColor("_OutlineColor", Color.white);
            Debug.Log("Assigned color: White");
        }
        else if (distance <= radarDisplay.maxDistance * 0.50f)
        {
            renderer.material.SetColor("_OutlineColor", Color.green);
            Debug.Log("Assigned color: Green");
        }
        else if (distance <= radarDisplay.maxDistance * 0.75f)
        {
            renderer.material.SetColor("_OutlineColor", Color.yellow);
            Debug.Log("Assigned color: Yellow");
        }
        else
        {
            renderer.material.SetColor("_OutlineColor", Color.red);
            Debug.Log("Assigned color: Red");
        }
    }
}
