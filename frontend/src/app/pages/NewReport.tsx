import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Textarea } from "../components/ui/textarea";
import { Label } from "../components/ui/label";
import { Input } from "../components/ui/input";
import { Slider } from "../components/ui/slider";
import { Activity, ArrowLeft, Send, Loader2, AlertCircle, Plus, X } from "lucide-react";
import { Progress } from "../components/ui/progress";
import { toast } from "sonner";
import { Alert, AlertDescription } from "../components/ui/alert";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../components/ui/select";
import { api } from "../utils/api";

interface SymptomCard {
  id: string;
  symptom: string;
  duration: string;
  severity: number;
}

export default function NewReport() {
  const navigate = useNavigate();
  const [symptomCards, setSymptomCards] = useState<SymptomCard[]>([
  ]);
  const [medicalImage, setMedicalImage] = useState<File | null>(null);
  const [medicalImagePreview, setMedicalImagePreview] = useState<string>("");
  const [gender, setGender] = useState<string>("");
  const [age, setAge] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [progress, setProgress] = useState(0);

  const addSymptomCard = () => {
    setSymptomCards([
      ...symptomCards,
      { id:Math.floor(Date.now()+0), symptom: "", duration: "", severity: 5 }
    ]);
  };

  const removeSymptomCard = (id: string) => {
    if (symptomCards.length > 1) {
      setSymptomCards(symptomCards.filter(card => card.id !== id));
    } else {
      toast.error("You must have at least one symptom");
    }
  };

  const updateSymptomCard = (id: string, field: keyof SymptomCard, value: string | number) => {
    setSymptomCards(symptomCards.map(card => 
      card.id === id ? { ...card, [field]: value } : card
    ));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate that at least one symptom is filled
    const validSymptoms = symptomCards.filter(card => card.symptom.trim() !== "");
    
    if (validSymptoms.length === 0) {
      toast.error("Please add at least one symptom");
      return;
    }

    // Check if all filled symptoms have duration
    const invalidSymptoms = validSymptoms.filter(card => !card.duration);
    if (invalidSymptoms.length > 0) {
      toast.error("Please specify duration for all symptoms");
      return;
    }

    setIsAnalyzing(true);
    setProgress(0);

    // Simulate progress
    const progressInterval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(progressInterval);
          return 90;
        }
        return prev + 10;
      });
    }, 300);

    try {
      const formData = new FormData();
      formData.append("username", localStorage.getItem("username") || "demo_user");
      formData.append("symptom_cards", JSON.stringify(validSymptoms));
      if (gender) {
        formData.append("gender", gender);
      }
      if (age) {
        formData.append("age", age);
      }
      if (medicalImage) {
        formData.append("medical_image", medicalImage);
      }
      const reportData = await api.post("predict/", formData);

      // if (!response.ok) {
      //   throw new Error(reportData.detail || "Failed to analyze symptoms");
      // }
      
      clearInterval(progressInterval);
      setProgress(100);

      // Save to localStorage for report details page
      const reportId = reportData.id || Date.now();
      localStorage.setItem(`report_${reportId}`, JSON.stringify(reportData));

      toast.success("Diagnosis complete!");
      
      setTimeout(() => {
        navigate(`/dashboard/report/${reportId}`);
      }, 500);
    } catch (error) {
      console.error("Diagnosis error:", error);
      clearInterval(progressInterval);
      setProgress(0);
      toast.error("Failed to analyze symptoms. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleMedicalImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    setMedicalImage(file);
    if (file) {
      setMedicalImagePreview(URL.createObjectURL(file));
      return;
    }
    setMedicalImagePreview("");
  };

  useEffect(() => {
    return () => {
      if (medicalImagePreview) {
        URL.revokeObjectURL(medicalImagePreview);
      }
    };
  }, [medicalImagePreview]);

  const durationOptions = [
    "Less than 1 day",
    "1-2 days",
    "3-5 days",
    "6-7 days",
    "1-2 weeks",
    "2-4 weeks",
    "1-3 months",
    "More than 3 months"
  ];

  const getSeverityColor = (severity: number) => {
    if (severity <= 3) return "text-green-600";
    if (severity <= 6) return "text-yellow-600";
    return "text-red-600";
  };

  const getSeverityLabel = (severity: number) => {
    if (severity <= 3) return "Mild";
    if (severity <= 6) return "Moderate";
    return "Severe";
  };

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
            <Link to="/dashboard">
              <Button variant="ghost">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Dashboard
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            New Diagnosis
          </h1>
          <p className="text-gray-600">
            Add your symptoms with duration and severity for an accurate AI analysis
          </p>
        </div>

        {/* Alert */}
        <Alert className="mb-6 border-blue-200 bg-blue-50">
          <AlertCircle className="h-4 w-4 text-blue-600" />
          <AlertDescription className="text-blue-900">
            <strong>Disclaimer:</strong> This is an AI-powered tool for
            educational purposes. Always consult a qualified healthcare
            professional for medical advice.
          </AlertDescription>
        </Alert>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Main Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Your Symptoms</CardTitle>
                <CardDescription>
                  Add one or more symptoms with their details
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid gap-4 md:grid-cols-2">
                    <div className="space-y-2">
                      <Label htmlFor="gender">Gender (optional)</Label>
                      <Select
                        value={gender}
                        onValueChange={setGender}
                        disabled={isAnalyzing}
                      >
                        <SelectTrigger id="gender" className="w-full">
                          <SelectValue placeholder="Select gender" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="male">Male</SelectItem>
                          <SelectItem value="female">Female</SelectItem>
                          <SelectItem value="other">Other</SelectItem>
                          <SelectItem value="prefer_not_to_say">Prefer not to say</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="age">Age (optional)</Label>
                      <Input
                        id="age"
                        type="number"
                        min={1}
                        max={150}
                        placeholder="Enter age"
                        value={age}
                        onChange={(e) => setAge(e.target.value)}
                        disabled={isAnalyzing}
                      />
                    </div>
                  </div>

                  {/* Symptom Cards */}
                  <div className="space-y-6">
                    {symptomCards.map((card, index) => (
                      <Card key={card.id} className="border-2 border-gray-200">
                        <CardHeader className="pb-4">
                          <div className="flex items-center justify-between">
                            <CardTitle className="text-lg">Symptom {index + 1}</CardTitle>
                            {symptomCards.length > 1 && (
                              <Button
                                type="button"
                                variant="ghost"
                                size="sm"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => removeSymptomCard(card.id)}
                                disabled={isAnalyzing}
                              >
                                <X className="w-4 h-4" />
                              </Button>
                            )}
                          </div>
                        </CardHeader>
                        <CardContent className="space-y-4">
                          {/* Symptom Description */}
                          <div className="space-y-2">
                            <Label htmlFor={`symptom-${card.id}`}>Symptom Description</Label>
                            <Input
                              id={`symptom-${card.id}`}
                              placeholder="e.g., Persistent headache, Fever, Sore throat"
                              value={card.symptom}
                              onChange={(e) => updateSymptomCard(card.id, "symptom", e.target.value)}
                              disabled={isAnalyzing}
                              className="w-full"
                            />
                          </div>

                          {/* Duration */}
                          <div className="space-y-2">
                            <Label htmlFor={`duration-${card.id}`}>Duration</Label>
                            <Select
                              value={card.duration}
                              onValueChange={(value) => updateSymptomCard(card.id, "duration", value)}
                              disabled={isAnalyzing}
                            >
                              <SelectTrigger id={`duration-${card.id}`} className="w-full">
                                <SelectValue placeholder="Select duration" />
                              </SelectTrigger>
                              <SelectContent>
                                {durationOptions.map(option => (
                                  <SelectItem key={option} value={option}>
                                    {option}
                                  </SelectItem>
                                ))}
                              </SelectContent>
                            </Select>
                          </div>

                          {/* Severity */}
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <Label htmlFor={`severity-${card.id}`}>Severity</Label>
                              <div className="text-right">
                                <span className={`text-sm font-medium ${getSeverityColor(card.severity)}`}>
                                  {card.severity}/10 - {getSeverityLabel(card.severity)}
                                </span>
                              </div>
                            </div>
                            <Slider
                              id={`severity-${card.id}`}
                              value={[card.severity]}
                              onValueChange={(value) => updateSymptomCard(card.id, "severity", value[0])}
                              disabled={isAnalyzing}
                              min={0}
                              max={10}
                              step={1}
                              className="w-full"
                            />
                            <div className="flex justify-between text-xs text-gray-500">
                              <span>No pain</span>
                              <span>Worst pain</span>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {/* Add Symptom Button */}
                  <Button
                    type="button"
                    variant="outline"
                    className="w-full border-2 border-dashed border-blue-300 text-blue-600 hover:bg-blue-50 hover:border-blue-400"
                    onClick={addSymptomCard}
                    disabled={isAnalyzing}
                  >
                    <Plus className="w-5 h-5 mr-2" />
                    Add Another Symptom
                  </Button>

                  <div className="space-y-2">
                    <Label htmlFor="medical-image">Medical Image (optional)</Label>
                    <Input
                      id="medical-image"
                      type="file"
                      accept="image/*,.pdf,.dcm"
                      onChange={handleMedicalImageChange}
                      disabled={isAnalyzing}
                    />
                    {medicalImagePreview && (
                      <img
                        src={medicalImagePreview}
                        alt="Medical upload preview"
                        className="h-36 w-full object-cover rounded-md border"
                      />
                    )}
                  </div>

                  {/* Progress */}
                  {isAnalyzing && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-600">
                          Analyzing symptoms...
                        </span>
                        <span className="font-medium text-blue-600">
                          {progress}%
                        </span>
                      </div>
                      <Progress value={progress} className="h-2" />
                    </div>
                  )}

                  {/* Submit Button */}
                  <Button
                    type="submit"
                    className="w-full bg-blue-600 hover:bg-blue-700"
                    size="lg"
                    disabled={isAnalyzing || symptomCards.every(card => card.symptom.trim().length === 0)}
                  >
                    {isAnalyzing ? (
                      <>
                        <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Send className="w-5 h-5 mr-2" />
                        Get Diagnosis
                      </>
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar - Tips */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">How to Use</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="space-y-1">
                    <h4 className="font-medium text-sm text-gray-900">
                      1. Add Symptoms
                    </h4>
                    <p className="text-sm text-gray-600">
                      Describe each symptom you're experiencing
                    </p>
                  </div>
                  <div className="space-y-1">
                    <h4 className="font-medium text-sm text-gray-900">
                      2. Select Duration
                    </h4>
                    <p className="text-sm text-gray-600">
                      Choose how long you've had the symptom
                    </p>
                  </div>
                  <div className="space-y-1">
                    <h4 className="font-medium text-sm text-gray-900">
                      3. Set Severity
                    </h4>
                    <p className="text-sm text-gray-600">
                      Use the slider (0-10) to indicate intensity
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Severity Scale</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  <span className="text-sm text-gray-700">0-3: Mild</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                  <span className="text-sm text-gray-700">4-6: Moderate</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-red-500"></div>
                  <span className="text-sm text-gray-700">7-10: Severe</span>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Tips</CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="text-sm text-gray-600 space-y-2">
                  <li>• Be specific about your symptoms</li>
                  <li>• Include location if applicable</li>
                  <li>• Mention any triggers or patterns</li>
                  <li>• Add multiple symptoms if needed</li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
