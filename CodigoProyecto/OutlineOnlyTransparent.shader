Shader "Custom/OutlineOnlyTransparent"
{
    Properties
    {
        _OutlineColor("Outline Color", Color) = (1,0,0,1) // Color del contorno
        _Outline("Outline width", Range(0.01, 0.1)) = 0.03 // Grosor del contorno
    }
    SubShader
    {
        Tags {"Queue" = "Overlay+1" "RenderType" = "Transparent"}
        LOD 100

        Pass
        {
            Name "OUTLINE"
            Tags {"LightMode" = "Always"}
            Cull Off // Renderizar ambas caras
            ZWrite On
            ZTest LEqual
            Blend SrcAlpha OneMinusSrcAlpha

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment frag
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
            };

            struct v2f
            {
                float4 pos : POSITION;
                float4 color : COLOR;
            };

            uniform float _Outline;
            uniform float4 _OutlineColor;

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                float3 norm = mul((float3x3) unity_ObjectToWorld, v.normal);
                o.pos.xy += norm.xy * _Outline;
                o.color = _OutlineColor;
                return o;
            }

            fixed4 frag(v2f i) : SV_Target
            {
                return i.color;
            }
            ENDCG
        }

        Pass
        {
            Name "BASE"
            Tags {"LightMode" = "Always"}
            Cull Off // Renderizar ambas caras
            ZWrite On
            ZTest LEqual
            Blend SrcAlpha OneMinusSrcAlpha

            CGPROGRAM
            #pragma vertex vert
            #pragma fragment fragBase
            #include "UnityCG.cginc"

            struct appdata
            {
                float4 vertex : POSITION;
                float3 normal : NORMAL;
            };

            struct v2f
            {
                float4 pos : POSITION;
            };

            v2f vert(appdata v)
            {
                v2f o;
                o.pos = UnityObjectToClipPos(v.vertex);
                return o;
            }

            fixed4 fragBase(v2f i) : SV_Target
            {
                return float4(0, 0, 0, 0); // Interior transparente
            }
            ENDCG
        }
    }
}
