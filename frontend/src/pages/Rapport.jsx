import React from 'react'
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Topbar from '../components/Topbar';

function Rapport() {
    const navigate = useNavigate();
    
    // Function to handle download button click
    //const handleDownload = (reportId) => {
      //console.log(Downloading report ${reportId});
      // In a real application, this would trigger a file download
      // You could make an API call to get the file or use a predefined URL
      //alert(Downloading Report ${reportId});
    //};
    
    const [reports, setReports] = useState([
        { id: 1, description: 'Rapport 1', userId: '#12548796', type: 'Shopping', date: '28 Jan, 12:30 AM' },
        { id: 2, description: 'Rapport 2', userId: '#12548796', type: 'Approvis', date: '25 Jan, 10:40 PM' },
        { id: 3, description: 'Rapport 3', userId: '#12548796', type: 'Service', date: '20 Jan, 10:40 PM' },
        { id: 4, description: 'Rapport 4', userId: '#12548796', type: 'Transfer', date: '15 Jan, 03:29 PM' },
        { id: 5, description: 'Rapport 5', userId: '#12548796', type: 'Transfer', date: '14 Jan, 10:40 PM' },
        { id: 6, description: 'Rapport 5', userId: '#12548796', type: 'Transfer', date: '14 Jan, 10:40 PM' },
    ]);
    
    return (
      // Main container - flex-1 makes it take available space
      <div className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Topbar - fixed height */}
        <Topbar pageTitle="Rapports" />
        
        {/* Content area - takes remaining height with overflow scroll */}
        <div className="flex-1 overflow-y-auto bg-gray-50">
          <div className="p-6">
            <div className="bg-white rounded-sm shadow-sm p-6">
              <div className="border-b border-gray-200 mb-6">
                <h2 className="text-blue-600 font-medium pb-2 inline-block border-b-2 border-blue-600">
                  Recent reports
                </h2>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="text-left text-gray-500">
                      <th className="py-3 px-4">Description</th>
                      <th className="py-3 px-4">User ID</th>
                      <th className="py-3 px-4">Type</th>
                      <th className="py-3 px-4">Date</th>
                      <th className="py-3 px-4 text-right">Receipt</th>
                    </tr>
                  </thead>
                  <tbody>
                    {reports.map((report) => (
                      <tr key={report.id}>
                        <td className="py-4 px-4 flex items-center">
                          <div className="h-6 w-6 rounded-full bg-gray-100 flex items-center justify-center mr-2">
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3 text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                            </svg>
                          </div>
                          {report.description}
                        </td>
                        <td className="py-4 px-4 text-gray-500">{report.userId}</td>
                        <td className="py-4 px-4">{report.type}</td>
                        <td className="py-4 px-4 text-gray-500">{report.date}</td>
                        <td className="py-4 px-4 text-right">
                          <button 
                            //onClick={() => handleDownload(report.id)} 
                            className="px-4 py-1 border border-blue-500 rounded-full text-blue-500 text-sm hover:bg-blue-50 transition-colors"
                          >
                            Download
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              
              <div className="mt-8 flex justify-end">
                <button 
                  onClick={() => navigate('/add-rapport')}
                  className="px-6 py-2 bg-orange-500 text-white rounded hover:bg-orange-600 transition-colors"
                >
                  Add
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
}

export default Rapport