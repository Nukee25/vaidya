import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Separator } from "../components/ui/separator";
import {
  Activity,
  ArrowLeft,
  AlertTriangle,
  CheckCircle,
  FileText,
  Calendar,
  Download,
  Share2,
} from "lucide-react";
import { toast } from "sonner";
import { api } from "../utils/api";

interface DiagnosisReport {
  diagnosis: string;
  predicted_diseases?: Array<{ disease: string; probability: number }>;
  severity: string;
  symptoms: string[];
  recommendations: string[];
  precautions: string[];
  medications?: string[];
  whenToSeeDoctor?: string;
  additionalInfo?: string;
  medicalImage?: string;
}

export default function ReportDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState<DiagnosisReport | null>(null);
  const [loading, setLoading] = useState(true);
  const getMedicalImageSrc = (medicalImage: string) => {
    if (medicalImage.startsWith("http://") || medicalImage.startsWith("https://") || medicalImage.startsWith("//")) {
      return medicalImage;
    }
    return medicalImage.startsWith("/") ? medicalImage : `/${medicalImage}`;
  };

  useEffect(() => {
    const username = localStorage.getItem("username");
    if (!username) {
      navigate("/auth");
      return;
    }
    if (!id) {
      setReport(null);
      setLoading(false);
      return;
    }
    api
      .get(`reports/${id}/?username=${encodeURIComponent(username)}`)
      .then((data) =>
        setReport(data && typeof data.diagnosis === "string" ? data : null)
      )
      .catch(() => setReport(null))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDownload = () => {
    toast.success("Report downloaded successfully");
  };

  const handleShare = () => {
    toast.success("Share link copied to clipboard");
  };

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case "mild":
        return "bg-green-100 text-green-700 hover:bg-green-100";
      case "moderate":
        return "bg-yellow-100 text-yellow-700 hover:bg-yellow-100";
      case "severe":
        return "bg-red-100 text-red-700 hover:bg-red-100";
      default:
        return "bg-gray-100 text-gray-700 hover:bg-gray-100";
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 text-blue-600 animate-pulse mx-auto mb-4" />
          <p className="text-gray-600">Loading report...</p>
        </div>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
        <Card className="max-w-md w-full mx-4">
          <CardContent className="pt-6 text-center">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">Report Not Found</h3>
            <p className="text-gray-600 mb-4">
              The requested report could not be found.
            </p>
            <Link to="/dashboard">
              <Button>Back to Dashboard</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Activity className="w-8 h-8 text-blue-600" />
              <span className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                Vaidya
              </span>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={handleShare}>
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </Button>
              <Button variant="outline" size="sm" onClick={handleDownload}>
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
              <Link to="/dashboard">
                <Button variant="ghost">
                  <ArrowLeft className="w-4 h-4 mr-2" />
                  Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Report Header */}
        <Card className="mb-6">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div>
                <CardTitle className="text-2xl mb-2">
                  Diagnosis Report
                </CardTitle>
                <CardDescription className="flex items-center gap-4">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {new Date().toLocaleDateString("en-US", {
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}
                  </span>
                  <span>Report ID: #{id}</span>
                </CardDescription>
              </div>
              <Badge className={getSeverityColor(report.severity)}>
                {report.severity} Severity
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <CheckCircle className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="font-semibold text-blue-900 mb-1">
                  Diagnosis
                </h3>
                <p className="text-blue-800">{report.diagnosis}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {report.predicted_diseases && report.predicted_diseases.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Top Predicted Diseases</CardTitle>
              <CardDescription>Top 3 probable conditions with confidence</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {report.predicted_diseases.slice(0, 3).map((prediction, index) => (
                  <div
                    key={`${prediction.disease}-${index}`}
                    className="flex items-center justify-between rounded-lg border border-gray-200 p-3"
                  >
                    <span className="font-medium text-gray-800">{prediction.disease}</span>
                    <Badge variant="secondary">{prediction.probability}%</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {report.medicalImage && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Submitted Medical Image</CardTitle>
            </CardHeader>
            <CardContent>
              <img
                src={getMedicalImageSrc(report.medicalImage)}
                alt="Submitted medical file"
                className="max-h-96 w-full rounded-lg border object-contain bg-white"
              />
            </CardContent>
          </Card>
        )}

        {/* Symptoms */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Identified Symptoms</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid sm:grid-cols-2 gap-3">
              {report?.symptoms?.map((symptom, index) => (
                <div
                  key={index}
                  className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg"
                >
                  <div className="w-2 h-2 bg-blue-600 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{symptom}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recommendations */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-green-600" />
              Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {report?.recommendations?.map((rec, index) => (
                <li key={index} className="flex items-start gap-3">
                  <span className="flex items-center justify-center w-6 h-6 bg-green-100 text-green-700 rounded-full text-sm font-medium flex-shrink-0">
                    {index + 1}
                  </span>
                  <span className="text-gray-700 pt-0.5">{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* Medications */}
        {report.medications && report.medications.length > 0 && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>Suggested Medications</CardTitle>
              <CardDescription>
                Over-the-counter options (consult a pharmacist or doctor)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {report?.medications?.map((med, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-3 p-3 border border-gray-200 rounded-lg"
                  >
                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                      <FileText className="w-4 h-4 text-purple-600" />
                    </div>
                    <span className="text-gray-700">{med}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Precautions */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-600" />
              Precautions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {report?.precautions?.map((precaution, index) => (
                <li key={index} className="flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{precaution}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        {/* When to See a Doctor */}
        {report.whenToSeeDoctor && (
          <Card className="mb-6 border-red-200 bg-red-50">
            <CardHeader>
              <CardTitle className="text-red-900 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" />
                When to See a Doctor
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-800">{report.whenToSeeDoctor}</p>
            </CardContent>
          </Card>
        )}

        {/* Additional Information */}
        {report.additionalInfo && (
          <Card>
            <CardHeader>
              <CardTitle>Additional Information</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-700">{report.additionalInfo}</p>
            </CardContent>
          </Card>
        )}

        <Separator className="my-8" />

        {/* Disclaimer */}
        <div className="text-center text-sm text-gray-500">
          <p className="mb-2">
            <strong>Medical Disclaimer:</strong> This AI-generated report is for
            informational purposes only and should not replace professional
            medical advice.
          </p>
          <p>
            Always consult with a qualified healthcare provider for proper
            diagnosis and treatment.
          </p>
        </div>
      </main>
    </div>
  );
}
