#!/usr/bin/env python3
"""
Automated Analysis Tools for Classifier Results

This script provides automated quality checking, consistency validation,
and reporting tools for the LLM-based literature classification system.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')


class ClassificationQualityChecker:
    """Quality checking and validation for classification results"""
    
    COUNTRY_KEYWORDS = ['usa', 'china', 'uk', 'germany', 'france', 'spain', 'italy', 
                        'brazil', 'india', 'global', 'worldwide']
    DISEASE_KEYWORDS = ['fever', 'virus', 'disease', 'cancer', 'infection']
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.issues = []
        
    def check_field_consistency(self, row: pd.Series) -> List[str]:
        """Check for consistency issues in a single row"""
        row_issues = []
        
        # Check if classification matches optimization field
        if row['classification'] == 'included':
            if row.get('optimization', '') in ['unknown', 'mentioned but not applied', 'none']:
                row_issues.append("Included but optimization unclear")
        
        # Check for data in wrong fields
        species_lower = str(row.get('species', '')).lower()
        for country in self.COUNTRY_KEYWORDS:
            if country in species_lower:
                row_issues.append(f"Possible country '{country}' in species field")
        
        # Check if disease is known but species is unknown
        disease = str(row.get('disease', '')).lower()
        species = str(row.get('species', '')).lower()
        if disease != 'unknown' and any(kw in disease for kw in self.DISEASE_KEYWORDS):
            if species == 'unknown':
                row_issues.append("Disease identified but species unknown")
        
        return row_issues
    
    def run_all_checks(self) -> pd.DataFrame:
        """Run all quality checks and add issues column"""
        self.df['quality_issues'] = self.df.apply(
            lambda row: '; '.join(self.check_field_consistency(row)), 
            axis=1
        )
        self.df['has_issues'] = self.df['quality_issues'].str.len() > 0
        return self.df
    
    def calculate_quality_metrics(self) -> Dict:
        """Calculate overall quality metrics"""
        metrics = {
            'total_articles': len(self.df),
            'articles_with_issues': self.df['has_issues'].sum(),
            'issue_rate': self.df['has_issues'].sum() / len(self.df),
        }
        
        # Calculate unknown rates for each field
        for field in ['species', 'disease', 'country', 'statistics', 'optimization', 'strategies']:
            if field in self.df.columns:
                unknown_count = (self.df[field].astype(str).str.lower() == 'unknown').sum()
                metrics[f'unknown_rate_{field}'] = unknown_count / len(self.df)
        
        # Calculate extraction completeness (inverse of unknown rate)
        unknown_fields = ['species', 'disease', 'country', 'statistics', 'optimization', 'strategies']
        available_fields = [f for f in unknown_fields if f in self.df.columns]
        if available_fields:
            total_cells = len(self.df) * len(available_fields)
            unknown_cells = sum(
                (self.df[field].astype(str).str.lower() == 'unknown').sum() 
                for field in available_fields
            )
            metrics['extraction_completeness'] = 1 - (unknown_cells / total_cells)
        
        return metrics


class PerformanceAnalyzer:
    """Analyze classification performance against human-classified data"""
    
    def __init__(self, classified_df: pd.DataFrame, human_df: pd.DataFrame = None):
        self.classified_df = classified_df.copy()
        self.human_df = human_df.copy() if human_df is not None else None
        
    def calculate_confusion_matrix(self) -> Dict:
        """Calculate confusion matrix if human classification is available"""
        if self.human_df is None or 'human' not in self.classified_df.columns:
            return None
        
        # Map classification to binary
        self.classified_df['pred'] = (
            self.classified_df['classification'].astype(str).str.lower() == 'included'
        ).astype(int)
        
        if 'human' not in self.classified_df.columns:
            return None
            
        true_labels = self.classified_df['human'].astype(int)
        pred_labels = self.classified_df['pred'].astype(int)
        
        tp = ((true_labels == 1) & (pred_labels == 1)).sum()
        tn = ((true_labels == 0) & (pred_labels == 0)).sum()
        fp = ((true_labels == 0) & (pred_labels == 1)).sum()
        fn = ((true_labels == 1) & (pred_labels == 0)).sum()
        
        total = len(self.classified_df)
        
        metrics = {
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'total': int(total)
        }
        
        # Calculate derived metrics
        if (tp + fn) > 0:
            metrics['sensitivity'] = tp / (tp + fn)
        else:
            metrics['sensitivity'] = np.nan
            
        if (tn + fp) > 0:
            metrics['specificity'] = tn / (tn + fp)
        else:
            metrics['specificity'] = np.nan
            
        if total > 0:
            metrics['accuracy'] = (tp + tn) / total
        else:
            metrics['accuracy'] = np.nan
            
        if (tp + fp) > 0:
            metrics['precision'] = tp / (tp + fp)
        else:
            metrics['precision'] = np.nan
            
        if (tp + fp) > 0 and (tp + fn) > 0:
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            if (precision + recall) > 0:
                metrics['f1_score'] = 2 * (precision * recall) / (precision + recall)
            else:
                metrics['f1_score'] = np.nan
        else:
            metrics['f1_score'] = np.nan
        
        return metrics


class ReportGenerator:
    """Generate comprehensive reports from classification results"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        
    def generate_summary_statistics(self) -> Dict:
        """Generate summary statistics for the classification"""
        included_df = self.df[
            self.df['classification'].astype(str).str.lower() == 'included'
        ]
        
        stats = {
            'total_articles': len(self.df),
            'included_count': len(included_df),
            'excluded_count': len(self.df) - len(included_df),
            'inclusion_rate': len(included_df) / len(self.df) if len(self.df) > 0 else 0
        }
        
        # Top categories for included articles
        for field in ['species', 'disease', 'country', 'statistics', 'optimization']:
            if field in included_df.columns:
                value_counts = included_df[field].value_counts().head(5)
                stats[f'top_{field}'] = value_counts.to_dict()
        
        return stats
    
    def generate_markdown_report(self, quality_metrics: Dict, 
                                 performance_metrics: Dict = None,
                                 summary_stats: Dict = None) -> str:
        """Generate a comprehensive markdown report"""
        report_lines = [
            "# Classification Results Report",
            "",
            "## Summary Statistics",
            ""
        ]
        
        if summary_stats:
            report_lines.extend([
                f"- **Total Articles:** {summary_stats.get('total_articles', 'N/A')}",
                f"- **Included:** {summary_stats.get('included_count', 'N/A')} ({summary_stats.get('inclusion_rate', 0)*100:.1f}%)",
                f"- **Excluded:** {summary_stats.get('excluded_count', 'N/A')}",
                ""
            ])
        
        report_lines.extend([
            "## Quality Metrics",
            ""
        ])
        
        if quality_metrics:
            report_lines.extend([
                f"- **Articles with Issues:** {quality_metrics.get('articles_with_issues', 'N/A')} ({quality_metrics.get('issue_rate', 0)*100:.1f}%)",
                f"- **Extraction Completeness:** {quality_metrics.get('extraction_completeness', 0)*100:.1f}%",
                "",
                "### Unknown Rates by Field:",
                ""
            ])
            
            for key, value in quality_metrics.items():
                if key.startswith('unknown_rate_'):
                    field = key.replace('unknown_rate_', '')
                    report_lines.append(f"- **{field.title()}:** {value*100:.1f}%")
            
            report_lines.append("")
        
        if performance_metrics:
            report_lines.extend([
                "## Performance Metrics (vs Human Classification)",
                "",
                f"- **Sensitivity (Recall):** {performance_metrics.get('sensitivity', 0)*100:.1f}%",
                f"- **Specificity:** {performance_metrics.get('specificity', 0)*100:.1f}%",
                f"- **Accuracy:** {performance_metrics.get('accuracy', 0)*100:.1f}%",
                f"- **Precision:** {performance_metrics.get('precision', 0)*100:.1f}%",
                f"- **F1 Score:** {performance_metrics.get('f1_score', 0)*100:.1f}%",
                "",
                "### Confusion Matrix:",
                "",
                f"- True Positives: {performance_metrics.get('true_positives', 'N/A')}",
                f"- True Negatives: {performance_metrics.get('true_negatives', 'N/A')}",
                f"- False Positives: {performance_metrics.get('false_positives', 'N/A')}",
                f"- False Negatives: {performance_metrics.get('false_negatives', 'N/A')}",
                ""
            ])
        
        if summary_stats:
            report_lines.extend([
                "## Top Categories (Included Articles)",
                ""
            ])
            
            for field in ['species', 'disease', 'country', 'statistics', 'optimization']:
                top_key = f'top_{field}'
                if top_key in summary_stats:
                    report_lines.extend([
                        f"### Top {field.title()}:",
                        ""
                    ])
                    for value, count in summary_stats[top_key].items():
                        report_lines.append(f"- {value}: {count}")
                    report_lines.append("")
        
        return '\n'.join(report_lines)
    
    def save_report(self, filename: str, quality_metrics: Dict, 
                   performance_metrics: Dict = None,
                   summary_stats: Dict = None):
        """Save report to file"""
        report = self.generate_markdown_report(
            quality_metrics, performance_metrics, summary_stats
        )
        with open(filename, 'w') as f:
            f.write(report)


def analyze_classification_results(classified_csv: str, 
                                   human_csv: str = None,
                                   output_report: str = 'analysis_report.md') -> Dict:
    """
    Main function to analyze classification results
    
    Args:
        classified_csv: Path to the classified papers CSV
        human_csv: Optional path to human-classified CSV for validation
        output_report: Path to save the markdown report
        
    Returns:
        Dictionary containing all metrics
    """
    # Load data
    df = pd.read_csv(classified_csv)
    print(f"Loaded {len(df)} classified articles")
    
    human_df = None
    if human_csv:
        human_df = pd.read_csv(human_csv, delimiter=';')
        print(f"Loaded {len(human_df)} human-classified articles")
        
        # Merge human classifications if available
        if 'PMID' in df.columns and 'PMID' in human_df.columns:
            df['PMID'] = df['PMID'].astype(str).str.strip()
            human_df['PMID'] = human_df['PMID'].astype(str).str.strip()
            
            # Add human classification column
            df['human'] = df['PMID'].isin(
                human_df.loc[human_df.get('Human', human_df.columns[0]) == 1, 'PMID']
            ).astype(int)
            print(f"Matched {df['human'].sum()} human-classified articles")
    
    # Run quality checks
    print("\nRunning quality checks...")
    checker = ClassificationQualityChecker(df)
    df = checker.run_all_checks()
    quality_metrics = checker.calculate_quality_metrics()
    
    # Analyze performance if human data available
    performance_metrics = None
    if human_df is not None and 'human' in df.columns:
        print("\nCalculating performance metrics...")
        analyzer = PerformanceAnalyzer(df, human_df)
        performance_metrics = analyzer.calculate_confusion_matrix()
    
    # Generate summary statistics
    print("\nGenerating summary statistics...")
    reporter = ReportGenerator(df)
    summary_stats = reporter.generate_summary_statistics()
    
    # Generate and save report
    print(f"\nGenerating report: {output_report}")
    reporter.save_report(
        output_report, 
        quality_metrics, 
        performance_metrics, 
        summary_stats
    )
    
    # Save enhanced CSV with quality checks
    output_csv = classified_csv.replace('.csv', '_with_quality_checks.csv')
    df.to_csv(output_csv, index=False)
    print(f"Saved enhanced CSV: {output_csv}")
    
    # Print summary to console
    print("\n" + "="*60)
    print("ANALYSIS SUMMARY")
    print("="*60)
    print(f"\nTotal Articles: {quality_metrics['total_articles']}")
    print(f"Articles with Issues: {quality_metrics['articles_with_issues']} ({quality_metrics['issue_rate']*100:.1f}%)")
    print(f"Extraction Completeness: {quality_metrics.get('extraction_completeness', 0)*100:.1f}%")
    
    if performance_metrics:
        print("\nPerformance vs Human Classification:")
        print(f"  Sensitivity: {performance_metrics['sensitivity']*100:.1f}%")
        print(f"  Specificity: {performance_metrics['specificity']*100:.1f}%")
        print(f"  Accuracy: {performance_metrics['accuracy']*100:.1f}%")
        print(f"  F1 Score: {performance_metrics.get('f1_score', 0)*100:.1f}%")
    
    print("\n" + "="*60)
    
    return {
        'quality_metrics': quality_metrics,
        'performance_metrics': performance_metrics,
        'summary_stats': summary_stats
    }


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python automated_analysis.py <classified_csv> [human_csv]")
        print("\nExample:")
        print("  python automated_analysis.py classified_papers_metric.csv human_classified.csv")
        sys.exit(1)
    
    classified_csv = sys.argv[1]
    human_csv = sys.argv[2] if len(sys.argv) > 2 else None
    
    results = analyze_classification_results(classified_csv, human_csv)
