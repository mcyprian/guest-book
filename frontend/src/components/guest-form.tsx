"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { api } from "@/lib/api";
import type { ConfigResponse, GuestCreate, ChildCreate } from "@/lib/types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

function emptyChild(position: number): ChildCreate {
  return { name: "", position };
}

export default function GuestForm() {
  const router = useRouter();
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const [stayFrom, setStayFrom] = useState("");
  const [stayTo, setStayTo] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [dateOfBirth, setDateOfBirth] = useState("");
  const [birthPlace, setBirthPlace] = useState("");
  const [nationality, setNationality] = useState("");
  const [permanentAddress, setPermanentAddress] = useState("");
  const [travelPurpose, setTravelPurpose] = useState("");
  const [passportNumber, setPassportNumber] = useState("");
  const [visaDetails, setVisaDetails] = useState("");
  const [accommodationName, setAccommodationName] = useState("");
  const [accommodationAddress, setAccommodationAddress] = useState("");
  const [children, setChildren] = useState<ChildCreate[]>([]);

  useEffect(() => {
    api.get<ConfigResponse>("/api/config").then((config) => {
      setAccommodationName(config.accommodation_name);
      setAccommodationAddress(config.accommodation_address);
    });
  }, []);

  function addChild() {
    if (children.length >= 4) return;
    setChildren([...children, emptyChild(children.length + 1)]);
  }

  function removeChild(index: number) {
    const updated = children
      .filter((_, i) => i !== index)
      .map((c, i) => ({ ...c, position: i + 1 }));
    setChildren(updated);
  }

  function updateChildName(index: number, name: string) {
    const updated = [...children];
    updated[index] = { ...updated[index], name };
    setChildren(updated);
  }

  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!stayFrom) errors.stay_from = "Required";
    if (!stayTo) errors.stay_to = "Required";
    if (stayFrom && stayTo && stayTo < stayFrom)
      errors.stay_to = "Must be on or after stay from date";
    if (!firstName.trim()) errors.first_name = "Required";
    if (!lastName.trim()) errors.last_name = "Required";
    if (!dateOfBirth) errors.date_of_birth = "Required";
    if (!birthPlace.trim()) errors.birth_place = "Required";
    if (!nationality.trim()) errors.nationality = "Required";
    if (!permanentAddress.trim()) errors.permanent_address = "Required";
    if (!travelPurpose.trim()) errors.travel_purpose = "Required";
    if (!passportNumber.trim()) errors.passport_number = "Required";
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    if (!validate()) return;
    setSubmitting(true);

    const payload: GuestCreate = {
      stay_from: stayFrom,
      stay_to: stayTo,
      first_name: firstName,
      last_name: lastName,
      date_of_birth: dateOfBirth,
      birth_place: birthPlace,
      nationality,
      permanent_address: permanentAddress,
      travel_purpose: travelPurpose,
      passport_number: passportNumber,
      visa_details: visaDetails || null,
      children: children.filter((c) => c.name.trim() !== ""),
    };

    try {
      await api.post("/api/guests", payload);
      toast.success("Guest record created");
      router.push("/guests");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create guest");
    } finally {
      setSubmitting(false);
    }
  }

  function fieldError(name: string) {
    return fieldErrors[name] ? (
      <p className="text-xs text-red-600">{fieldErrors[name]}</p>
    ) : null;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {error && (
        <div className="rounded bg-red-50 p-3 text-sm text-red-600">
          {error}
        </div>
      )}

      {/* Stay dates */}
      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="px-2 font-semibold">Stay Period (Pobyt)</legend>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="stay_from">Stay from (Pobyt od)</Label>
            <Input
              id="stay_from"
              type="date"
              value={stayFrom}
              onChange={(e) => setStayFrom(e.target.value)}
              required
              className={fieldErrors.stay_from ? "border-red-500" : ""}
            />
            {fieldError("stay_from")}
          </div>
          <div className="space-y-2">
            <Label htmlFor="stay_to">Stay to (Pobyt do)</Label>
            <Input
              id="stay_to"
              type="date"
              value={stayTo}
              onChange={(e) => setStayTo(e.target.value)}
              required
              className={fieldErrors.stay_to ? "border-red-500" : ""}
            />
            {fieldError("stay_to")}
          </div>
        </div>
      </fieldset>

      {/* Personal info */}
      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="px-2 font-semibold">Personal Information</legend>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="first_name">1. First name (Meno)</Label>
            <Input
              id="first_name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
              className={fieldErrors.first_name ? "border-red-500" : ""}
            />
            {fieldError("first_name")}
          </div>
          <div className="space-y-2">
            <Label htmlFor="last_name">2. Surname (Priezvisko)</Label>
            <Input
              id="last_name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
              className={fieldErrors.last_name ? "border-red-500" : ""}
            />
            {fieldError("last_name")}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="date_of_birth">
              3. Date of birth (Datum narodenia)
            </Label>
            <Input
              id="date_of_birth"
              type="date"
              value={dateOfBirth}
              onChange={(e) => setDateOfBirth(e.target.value)}
              required
              className={fieldErrors.date_of_birth ? "border-red-500" : ""}
            />
            {fieldError("date_of_birth")}
          </div>
          <div className="space-y-2">
            <Label htmlFor="birth_place">
              3. Place of birth incl. state (Miesto narodenia, stat)
            </Label>
            <Input
              id="birth_place"
              value={birthPlace}
              onChange={(e) => setBirthPlace(e.target.value)}
              required
              className={fieldErrors.birth_place ? "border-red-500" : ""}
            />
            {fieldError("birth_place")}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="nationality">
              4. Nationality (Statna prislusnost)
            </Label>
            <Input
              id="nationality"
              value={nationality}
              onChange={(e) => setNationality(e.target.value)}
              required
              className={fieldErrors.nationality ? "border-red-500" : ""}
            />
            {fieldError("nationality")}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="permanent_address">
            5. Permanent address (Trvaly pobyt v domovskom state)
          </Label>
          <Input
            id="permanent_address"
            value={permanentAddress}
            onChange={(e) => setPermanentAddress(e.target.value)}
            required
            className={fieldErrors.permanent_address ? "border-red-500" : ""}
          />
          {fieldError("permanent_address")}
        </div>
      </fieldset>

      {/* Travel info */}
      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="px-2 font-semibold">Travel Details</legend>

        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="travel_purpose">
              6. Purpose of travel (Ucel cesty do SR)
            </Label>
            <Input
              id="travel_purpose"
              value={travelPurpose}
              onChange={(e) => setTravelPurpose(e.target.value)}
              required
              className={fieldErrors.travel_purpose ? "border-red-500" : ""}
            />
            {fieldError("travel_purpose")}
          </div>
          <div className="space-y-2">
            <Label htmlFor="passport_number">
              7. Passport number (Cislo pasu)
            </Label>
            <Input
              id="passport_number"
              value={passportNumber}
              onChange={(e) => setPassportNumber(e.target.value)}
              required
              className={fieldErrors.passport_number ? "border-red-500" : ""}
            />
            {fieldError("passport_number")}
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="visa_details">
            8. Visa / EU residence permit details (optional)
          </Label>
          <Input
            id="visa_details"
            value={visaDetails}
            onChange={(e) => setVisaDetails(e.target.value)}
          />
        </div>
      </fieldset>

      {/* Accommodation */}
      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="px-2 font-semibold">
          9. Accommodation (Ubytovacie zariadenie)
        </legend>
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Name</Label>
            <Input value={accommodationName} disabled />
          </div>
          <div className="space-y-2">
            <Label>Address</Label>
            <Input value={accommodationAddress} disabled />
          </div>
        </div>
      </fieldset>

      {/* Children */}
      <fieldset className="space-y-4 rounded-lg border p-4">
        <legend className="px-2 font-semibold">
          10. Accompanying children (Spolucestujuce deti)
        </legend>
        {children.map((child, index) => (
          <div key={index} className="flex items-end gap-2">
            <div className="flex-1 space-y-2">
              <Label>{index + 1}. Child name</Label>
              <Input
                value={child.name}
                onChange={(e) => updateChildName(index, e.target.value)}
              />
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => removeChild(index)}
            >
              Remove
            </Button>
          </div>
        ))}
        {children.length < 4 && (
          <Button type="button" variant="outline" size="sm" onClick={addChild}>
            + Add child
          </Button>
        )}
      </fieldset>

      <div className="flex gap-4">
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving..." : "Save Guest"}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={() => router.push("/guests")}
        >
          Cancel
        </Button>
      </div>
    </form>
  );
}
