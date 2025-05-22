import React from 'react'
import { useState } from 'react';
import { Search, Paperclip } from 'lucide-react';
import Topbar from '../components/Topbar';

function AjouterRapport() {
    const [objectText, setObjectText] = useState('');
    const [descriptionText, setDescriptionText] = useState('');
  return (
     // Main container - flex-1 makes it take available space
     <div className="flex-1 flex flex-col h-screen overflow-hidden">
     {/* Topbar - fixed height */}
     <Topbar pageTitle="New Rapport" />
     
     {/* Content area - takes remaining height with overflow scroll */}
     <div className="flex-1 overflow-y-auto bg-gray-50">
       <div className="flex flex-col p-4 w-full max-w-4xl mx-auto">
         {/* Header with tab */}
         <div className="mb-6">
           <div className="border-b border-gray-200">
             <div className="w-20">
               <button className="py-2 px-1 text-blue-600 border-b-2 border-blue-600 font-medium text-sm">
                 Rapport
               </button>
             </div>
           </div>
         </div>

         {/* Import button */}
         <div className="flex justify-center mb-8">
           <button className="bg-orange-400 hover:bg-orange-500 text-white font-medium py-3 px-6 rounded-md transition duration-200">
             Importer Rapport
           </button>
         </div>

         {/* Problem section */}
         <div className="mb-8">
           <h2 className="text-red-500 font-medium mb-4">Introduire Problèmes</h2>
           
           {/* Search fields */}
           <div className="mb-4">
             <div className="relative mb-3">
               <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                 <Search className="w-4 h-4 text-gray-500" />
               </div>
               <input 
                 type="search" 
                 className="w-full pl-10 py-3 px-4 bg-white border border-gray-200 rounded-md text-sm text-gray-500"
                 placeholder="Selectionner la phase et l'operation concernées" 
               />
             </div>

             <div className="relative">
               <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                 <Search className="w-4 h-4 text-gray-500" />
               </div>
               <input 
                 type="search" 
                 className="w-full pl-10 py-3 px-4 bg-white border border-gray-200 rounded-md text-sm text-gray-500"
                 placeholder="Chercher un ancien probleme" 
               />
             </div>
           </div>
           
           {/* Problem form */}
           <div className="bg-white p-6 rounded-md shadow-sm border border-gray-100">
             <div className="mb-3">
               <p className="font-medium mb-2">Object:</p>
               <textarea 
                 className="w-full min-h-[40px] p-2 border border-gray-200 rounded-md resize-none"
                 value={objectText}
                 onChange={(e) => setObjectText(e.target.value)}
               />
             </div>
             
             <div className="mb-3">
               <p className="font-medium mb-2">Description:</p>
               <textarea 
                 className="w-full min-h-[80px] p-2 border border-gray-200 rounded-md resize-none"
                 value={descriptionText}
                 onChange={(e) => setDescriptionText(e.target.value)}
               />
             </div>
             
             <div className="flex justify-end">
               <button className="p-2 text-gray-500 hover:bg-gray-100 rounded-full">
                 <Paperclip className="w-5 h-5" />
               </button>
             </div>
           </div>
         </div>

         {/* Validate button */}
         <div className="flex justify-end mb-6">
           <button className="bg-orange-400 hover:bg-orange-500 text-white font-medium py-3 px-8 rounded-md transition duration-200">
             Valider
           </button>
         </div>
       </div>
     </div>
   </div>
  )
}

export default AjouterRapport