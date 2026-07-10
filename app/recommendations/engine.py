"""Recommendation Engine"""

from typing import List, Optional

from app.schemas.analysis import (
    AcneSeverity,
    IngredientRecommendation,
    PigmentationLevel,
    PoreSize,
    RednessLevel,
    SkinType,
    WrinkleLevel
)


class RecommendationEngine:
    """
    Rule-based recommendation engine for skincare ingredients.
    
    Generates personalized ingredient recommendations based on
    analysis results using deterministic rules.
    """
    
    # Supported ingredients with their properties
    INGREDIENTS = {
        "Niacinamide": {
            "benefits": [
                "Regulates oil production",
                "Reduces enlarged pores",
                "Improves skin barrier",
                "Reduces redness",
                "Evens skin tone"
            ],
            "suitable_for": [
                SkinType.OILY,
                SkinType.COMBINATION,
                SkinType.NORMAL
            ],
            "addresses": [
                "oiliness",
                "pores",
                "redness",
                "pigmentation"
            ],
            "frequency": "Daily (AM/PM)",
            "notes": "Well-tolerated by most skin types. Start with 2-5% concentration.",
            "precautions": "Generally safe, but may cause mild irritation in sensitive skin."
        },
        "Salicylic Acid (BHA)": {
            "benefits": [
                "Exfoliates inside pores",
                "Reduces acne",
                "Unclogs pores",
                "Reduces blackheads",
                "Anti-inflammatory"
            ],
            "suitable_for": [
                SkinType.OILY,
                SkinType.COMBINATION
            ],
            "addresses": [
                "acne",
                "oiliness",
                "pores"
            ],
            "frequency": "2-3 times per week, gradually increasing to daily",
            "notes": "Oil-soluble, works inside pores. Use 0.5-2% concentration.",
            "precautions": "Can be drying. Use sunscreen. Avoid if pregnant. Don't combine with other strong acids."
        },
        "Glycolic Acid (AHA)": {
            "benefits": [
                "Exfoliates surface skin",
                "Improves texture",
                "Brightens skin",
                "Reduces fine lines",
                "Improves pigmentation"
            ],
            "suitable_for": [
                SkinType.DRY,
                SkinType.NORMAL,
                SkinType.COMBINATION
            ],
            "addresses": [
                "texture",
                "pigmentation",
                "wrinkles"
            ],
            "frequency": "2-3 times per week, gradually increasing",
            "notes": "Water-soluble, works on surface. Use 5-10% concentration.",
            "precautions": "Increases sun sensitivity. Use sunscreen. Can irritate sensitive skin."
        },
        "Hyaluronic Acid": {
            "benefits": [
                "Hydrates skin",
                "Plumps skin",
                "Improves elasticity",
                "Reduces fine lines",
                "Soothes skin"
            ],
            "suitable_for": [
                SkinType.DRY,
                SkinType.NORMAL,
                SkinType.OILY,
                SkinType.COMBINATION
            ],
            "addresses": [
                "hydration",
                "texture",
                "wrinkles"
            ],
            "frequency": "Daily (AM/PM)",
            "notes": "Works for all skin types. Can be layered with other products.",
            "precautions": "None known. Patch test if you have very sensitive skin."
        },
        "Vitamin C": {
            "benefits": [
                "Brightens skin",
                "Antioxidant protection",
                "Boosts collagen",
                "Improves pigmentation",
                "Evens skin tone"
            ],
            "suitable_for": [
                SkinType.NORMAL,
                SkinType.DRY,
                SkinType.COMBINATION
            ],
            "addresses": [
                "pigmentation",
                "redness",
                "wrinkles"
            ],
            "frequency": "Daily (AM)",
            "notes": "Best used in the morning for antioxidant protection. Use 10-20% concentration.",
            "precautions": "Can cause irritation in sensitive skin. May increase sun sensitivity."
        },
        "Ceramides": {
            "benefits": [
                "Strengthens skin barrier",
                "Retains moisture",
                "Soothes irritated skin",
                "Protects against environmental damage"
            ],
            "suitable_for": [
                SkinType.DRY,
                SkinType.NORMAL
            ],
            "addresses": [
                "hydration",
                "barrier",
                "redness"
            ],
            "frequency": "Daily (AM/PM)",
            "notes": "Essential for dry or sensitive skin. Can be used with all skin types.",
            "precautions": "None known."
        },
        "Retinol": {
            "benefits": [
                "Reduces wrinkles",
                "Improves texture",
                "Increases cell turnover",
                "Reduces acne",
                "Improves pigmentation"
            ],
            "suitable_for": [
                SkinType.NORMAL,
                SkinType.DRY,
                SkinType.COMBINATION
            ],
            "addresses": [
                "wrinkles",
                "texture",
                "pigmentation",
                "acne"
            ],
            "frequency": "Start with 2-3 times per week, increase to daily",
            "notes": "Start with low concentration (0.25-0.5%). Use at night.",
            "precautions": "Can cause irritation, redness, and peeling. Increases sun sensitivity. Avoid if pregnant. Don't combine with strong acids."
        },
        "Azelaic Acid": {
            "benefits": [
                "Reduces acne",
                "Improves pigmentation",
                "Reduces redness",
                "Exfoliates gently",
                "Anti-inflammatory"
            ],
            "suitable_for": [
                SkinType.OILY,
                SkinType.COMBINATION,
                SkinType.NORMAL
            ],
            "addresses": [
                "acne",
                "pigmentation",
                "redness"
            ],
            "frequency": "Daily (AM/PM)",
            "notes": "Gentle and well-tolerated. Use 10-20% concentration.",
            "precautions": "Generally safe, but may cause mild irritation initially."
        },
        "Sunscreen": {
            "benefits": [
                "Protects from UV damage",
                "Prevents premature aging",
                "Prevents pigmentation",
                "Prevents skin cancer"
            ],
            "suitable_for": [
                SkinType.OILY,
                SkinType.DRY,
                SkinType.NORMAL,
                SkinType.COMBINATION
            ],
            "addresses": [
                "prevention",
                "pigmentation",
                "wrinkles"
            ],
            "frequency": "Daily (AM), reapply every 2 hours when exposed to sun",
            "notes": "Essential for all skin types and concerns. Use broad-spectrum SPF 30-50.",
            "precautions": "None. Essential for skin health."
        }
    }
    
    # Priority levels
    PRIORITY_HIGH = "High"
    PRIORITY_MEDIUM = "Medium"
    PRIORITY_LOW = "Low"
    
    def __init__(self):
        self.ingredient_db = self.INGREDIENTS
        
    def generate_recommendations(
        self,
        skin_type: SkinType,
        oiliness: int,
        hydration: int,
        redness: RednessLevel,
        pigmentation: PigmentationLevel,
        acne_severity: AcneSeverity,
        wrinkles: WrinkleLevel,
        pores: PoreSize,
        texture: Optional[int] = None,
        acne_count: Optional[int] = None
    ) -> List[IngredientRecommendation]:
        """
        Generate ingredient recommendations based on analysis results.
        
        Args:
            skin_type: Detected skin type
            oiliness: Oiliness score (0-100)
            hydration: Hydration score (0-100)
            redness: Redness level
            pigmentation: Pigmentation level
            acne_severity: Acne severity
            wrinkles: Wrinkles level
            pores: Pore size
            texture: Optional texture smoothness score
            acne_count: Optional acne lesion count
            
        Returns:
            List of IngredientRecommendation objects
        """
        recommendations = []
        
        # Always recommend sunscreen
        recommendations.append(self._create_recommendation(
            "Sunscreen",
            self.PRIORITY_HIGH,
            "Essential for protecting skin from UV damage and preventing premature aging",
            self.ingredient_db["Sunscreen"]["frequency"],
            self.ingredient_db["Sunscreen"]["notes"],
            self.ingredient_db["Sunscreen"]["precautions"]
        ))
        
        # Add recommendations based on skin concerns
        
        # Oiliness
        if oiliness > 70:
            recommendations.append(self._create_recommendation(
                "Niacinamide",
                self.PRIORITY_HIGH,
                "Helps regulate excess oil production and improve the appearance of enlarged pores.",
                self.ingredient_db["Niacinamide"]["frequency"],
                self.ingredient_db["Niacinamide"]["notes"],
                self.ingredient_db["Niacinamide"]["precautions"]
            ))
            
            if pores == PoreSize.LARGE:
                recommendations.append(self._create_recommendation(
                    "Salicylic Acid (BHA)",
                    self.PRIORITY_MEDIUM,
                    "Exfoliates inside pores to unclog them and reduce their appearance.",
                    self.ingredient_db["Salicylic Acid (BHA)"]["frequency"],
                    self.ingredient_db["Salicylic Acid (BHA)"]["notes"],
                    self.ingredient_db["Salicylic Acid (BHA)"]["precautions"]
                ))
        
        # Dryness
        if hydration < 40:
            recommendations.append(self._create_recommendation(
                "Hyaluronic Acid",
                self.PRIORITY_HIGH,
                "Provides intense hydration and helps plump the skin.",
                self.ingredient_db["Hyaluronic Acid"]["frequency"],
                self.ingredient_db["Hyaluronic Acid"]["notes"],
                self.ingredient_db["Hyaluronic Acid"]["precautions"]
            ))
            
            recommendations.append(self._create_recommendation(
                "Ceramides",
                self.PRIORITY_HIGH,
                "Strengthens the skin barrier to prevent moisture loss.",
                self.ingredient_db["Ceramides"]["frequency"],
                self.ingredient_db["Ceramides"]["notes"],
                self.ingredient_db["Ceramides"]["precautions"]
            ))
        
        # Redness
        if redness != RednessLevel.LOW:
            recommendations.append(self._create_recommendation(
                "Niacinamide",
                self.PRIORITY_MEDIUM if oiliness > 70 else self.PRIORITY_HIGH,
                "Reduces redness and calms irritated skin.",
                self.ingredient_db["Niacinamide"]["frequency"],
                self.ingredient_db["Niacinamide"]["notes"],
                self.ingredient_db["Niacinamide"]["precautions"]
            ))
            
            if redness == RednessLevel.HIGH:
                recommendations.append(self._create_recommendation(
                    "Azelaic Acid",
                    self.PRIORITY_MEDIUM,
                    "Reduces inflammation and calms red, irritated skin.",
                    self.ingredient_db["Azelaic Acid"]["frequency"],
                    self.ingredient_db["Azelaic Acid"]["notes"],
                    self.ingredient_db["Azelaic Acid"]["precautions"]
                ))
        
        # Pigmentation
        if pigmentation != PigmentationLevel.NONE:
            if pigmentation == PigmentationLevel.SEVERE:
                priority = self.PRIORITY_HIGH
            elif pigmentation == PigmentationLevel.MODERATE:
                priority = self.PRIORITY_MEDIUM
            else:
                priority = self.PRIORITY_LOW
            
            recommendations.append(self._create_recommendation(
                "Vitamin C",
                priority,
                "Brightens skin and helps fade dark spots and uneven pigmentation.",
                self.ingredient_db["Vitamin C"]["frequency"],
                self.ingredient_db["Vitamin C"]["notes"],
                self.ingredient_db["Vitamin C"]["precautions"]
            ))
            
            recommendations.append(self._create_recommendation(
                "Azelaic Acid",
                priority,
                "Helps reduce the appearance of dark spots and hyperpigmentation.",
                self.ingredient_db["Azelaic Acid"]["frequency"],
                self.ingredient_db["Azelaic Acid"]["notes"],
                self.ingredient_db["Azelaic Acid"]["precautions"]
            ))
            
            if pigmentation in [PigmentationLevel.MODERATE, PigmentationLevel.SEVERE]:
                recommendations.append(self._create_recommendation(
                    "Glycolic Acid (AHA)",
                    self.PRIORITY_MEDIUM,
                    "Exfoliates the skin surface to improve the appearance of pigmentation.",
                    self.ingredient_db["Glycolic Acid (AHA)"]["frequency"],
                    self.ingredient_db["Glycolic Acid (AHA)"]["notes"],
                    self.ingredient_db["Glycolic Acid (AHA)"]["precautions"]
                ))
        
        # Acne
        if acne_severity != AcneSeverity.NONE:
            if acne_severity == AcneSeverity.SEVERE:
                priority = self.PRIORITY_HIGH
            else:
                priority = self.PRIORITY_MEDIUM
            
            recommendations.append(self._create_recommendation(
                "Salicylic Acid (BHA)",
                priority,
                "Exfoliates inside pores to prevent and treat acne breakouts.",
                self.ingredient_db["Salicylic Acid (BHA)"]["frequency"],
                self.ingredient_db["Salicylic Acid (BHA)"]["notes"],
                self.ingredient_db["Salicylic Acid (BHA)"]["precautions"]
            ))
            
            recommendations.append(self._create_recommendation(
                "Azelaic Acid",
                priority,
                "Reduces acne-causing bacteria and inflammation.",
                self.ingredient_db["Azelaic Acid"]["frequency"],
                self.ingredient_db["Azelaic Acid"]["notes"],
                self.ingredient_db["Azelaic Acid"]["precautions"]
            ))
            
            if acne_severity == AcneSeverity.SEVERE:
                recommendations.append(self._create_recommendation(
                    "Retinol",
                    self.PRIORITY_MEDIUM,
                    "Increases cell turnover to prevent clogged pores and acne formation.",
                    self.ingredient_db["Retinol"]["frequency"],
                    self.ingredient_db["Retinol"]["notes"],
                    self.ingredient_db["Retinol"]["precautions"]
                ))
        
        # Wrinkles
        if wrinkles != WrinkleLevel.MINIMAL:
            recommendations.append(self._create_recommendation(
                "Retinol",
                self.PRIORITY_MEDIUM if wrinkles == WrinkleLevel.SEVERE else self.PRIORITY_LOW,
                "Stimulates collagen production to reduce the appearance of fine lines and wrinkles.",
                self.ingredient_db["Retinol"]["frequency"],
                self.ingredient_db["Retinol"]["notes"],
                self.ingredient_db["Retinol"]["precautions"]
            ))
            
            if wrinkles in [WrinkleLevel.MODERATE, WrinkleLevel.SEVERE]:
                recommendations.append(self._create_recommendation(
                    "Vitamin C",
                    self.PRIORITY_MEDIUM,
                    "Boosts collagen production and protects against free radical damage that causes aging.",
                    self.ingredient_db["Vitamin C"]["frequency"],
                    self.ingredient_db["Vitamin C"]["notes"],
                    self.ingredient_db["Vitamin C"]["precautions"]
                ))
            
            recommendations.append(self._create_recommendation(
                "Hyaluronic Acid",
                self.PRIORITY_MEDIUM if wrinkles == WrinkleLevel.SEVERE else self.PRIORITY_LOW,
                "Plumps the skin to temporarily reduce the appearance of fine lines.",
                self.ingredient_db["Hyaluronic Acid"]["frequency"],
                self.ingredient_db["Hyaluronic Acid"]["notes"],
                self.ingredient_db["Hyaluronic Acid"]["precautions"]
            ))
        
        # Pores
        if pores == PoreSize.LARGE:
            if not any(r.ingredient == "Niacinamide" for r in recommendations):
                recommendations.append(self._create_recommendation(
                    "Niacinamide",
                    self.PRIORITY_MEDIUM,
                    "Helps minimize the appearance of enlarged pores.",
                    self.ingredient_db["Niacinamide"]["frequency"],
                    self.ingredient_db["Niacinamide"]["notes"],
                    self.ingredient_db["Niacinamide"]["precautions"]
                ))
            
            if not any(r.ingredient == "Salicylic Acid (BHA)" for r in recommendations):
                recommendations.append(self._create_recommendation(
                    "Salicylic Acid (BHA)",
                    self.PRIORITY_MEDIUM,
                    "Unclogs pores to reduce their appearance.",
                    self.ingredient_db["Salicylic Acid (BHA)"]["frequency"],
                    self.ingredient_db["Salicylic Acid (BHA)"]["notes"],
                    self.ingredient_db["Salicylic Acid (BHA)"]["precautions"]
                ))
        
        # Texture
        if texture is not None and texture < 50:
            recommendations.append(self._create_recommendation(
                "Glycolic Acid (AHA)",
                self.PRIORITY_MEDIUM,
                "Exfoliates to improve skin texture and smoothness.",
                self.ingredient_db["Glycolic Acid (AHA)"]["frequency"],
                self.ingredient_db["Glycolic Acid (AHA)"]["notes"],
                self.ingredient_db["Glycolic Acid (AHA)"]["precautions"]
            ))
        
        # Remove duplicates and sort by priority
        unique_recommendations = {}
        for rec in recommendations:
            if rec.ingredient not in unique_recommendations:
                unique_recommendations[rec.ingredient] = rec
            else:
                # Keep the higher priority one
                existing = unique_recommendations[rec.ingredient]
                if self._priority_to_int(rec.priority) > self._priority_to_int(existing.priority):
                    unique_recommendations[rec.ingredient] = rec
        
        # Sort by priority
        priority_order = {self.PRIORITY_HIGH: 0, self.PRIORITY_MEDIUM: 1, self.PRIORITY_LOW: 2}
        sorted_recommendations = sorted(
            unique_recommendations.values(),
            key=lambda r: (priority_order.get(r.priority, 2), r.ingredient)
        )
        
        return sorted_recommendations
    
    def _create_recommendation(
        self,
        ingredient: str,
        priority: str,
        reason: str,
        frequency: str,
        notes: str,
        precautions: str
    ) -> IngredientRecommendation:
        """Create a recommendation object"""
        return IngredientRecommendation(
            ingredient=ingredient,
            priority=priority,
            reason=reason,
            suggested_frequency=frequency,
            usage_notes=notes,
            precautions=precautions
        )
    
    def _priority_to_int(self, priority: str) -> int:
        """Convert priority string to integer for comparison"""
        return {
            self.PRIORITY_HIGH: 3,
            self.PRIORITY_MEDIUM: 2,
            self.PRIORITY_LOW: 1
        }.get(priority, 0)
