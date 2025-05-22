import { useState } from 'react';

export default function ProgressBars({ delaiProgress, coutProgress }) {
  // Données reçues en props:
  delaiProgress = { value: 50, max: 100, unit: 'Days' };
  coutProgress = { value: 7.2, max: 10, unit: 'M $' };
  
  // Fonction pour déterminer la couleur en fonction de la progression
  const getProgressColor = (value, max) => {
    const percentage = (value / max) * 100;
    
    if (percentage < 30) return 'bg-red-500'; // En retard ou sous-budgété (moins de 30%)
    if (percentage < 70) return 'bg-yellow-400'; // En cours (entre 30% et 70%)
    if (percentage <= 90) return 'bg-green-500'; // Bien avancé (entre 70% et 90%)
    return 'bg-red-500'; // Dépassement possible (plus de 90%)
  };

  // Calcul des pourcentages pour l'affichage
  const delaiPercentage = Math.min(100, Math.round((delaiProgress.value / delaiProgress.max) * 100));
  const coutPercentage = Math.min(100, Math.round((coutProgress.value / coutProgress.max) * 100));
  
  // Couleurs dynamiques
  const delaiColor = getProgressColor(delaiProgress.value, delaiProgress.max);
  const coutColor = getProgressColor(coutProgress.value, coutProgress.max);

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm">
      {/* Barre de progression délai */}
      <h2 className="text-lg font-medium mb-4">Délais Progress</h2>
      <div className="mb-2 flex justify-between">
        <span>{delaiProgress.value} {delaiProgress.unit}</span>
        <span className="text-sm text-gray-500">
          {delaiPercentage}% of {delaiProgress.max} {delaiProgress.unit}
        </span>
      </div>
      <div className="w-full bg-gray-200 h-2 rounded-full mb-6">
        <div 
          className={`h-2 rounded-full ${delaiColor}`}
          style={{ width: `${delaiPercentage}%` }}
        ></div>
      </div>
      
      {/* Barre de progression coût */}
      <h2 className="text-lg font-medium mb-4">Cout Progress</h2>
      <div className="mb-2 flex justify-between">
        <span>{coutProgress.value} {coutProgress.unit}</span>
        <span className="text-sm text-gray-500">
          {coutPercentage}% of {coutProgress.max} {coutProgress.unit}
        </span>
      </div>
      <div className="w-full bg-gray-200 h-2 rounded-full">
        <div 
          className={`h-2 rounded-full ${coutColor}`}
          style={{ width: `${coutPercentage}%` }}
        ></div>
      </div>
    </div>
  );
}